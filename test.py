import argparse
import cv2
import numpy as np
import os
import torch
from torch import nn
from torch.nn import functional as F
import torchgeometry as tgm

from datasets import VITONDataset, VITONDataLoader
from network import SegGenerator, GMM, ALIASGenerator
from utils import gen_noise, load_checkpoint, save_images


def get_opt():
    parser = argparse.ArgumentParser()
    parser.add_argument('--name', type=str, required=True)

    parser.add_argument('-b', '--batch_size', type=int, default=1)
    parser.add_argument('-j', '--workers', type=int, default=1)
    parser.add_argument('--load_height', type=int, default=1024)
    parser.add_argument('--load_width', type=int, default=768)
    parser.add_argument('--shuffle', action='store_true')

    parser.add_argument('--dataset_dir', type=str, default='/content/inputs')
    parser.add_argument('--dataset_mode', type=str, default='test')
    parser.add_argument('--dataset_list', type=str, default='test_pairs.txt')
    parser.add_argument('--checkpoint_dir', type=str, default='/content/virtual_clothes_try_on_assistant/checkpoints')
    parser.add_argument('--save_dir', type=str, default='/content')

    parser.add_argument('--display_freq', type=int, default=1)

    parser.add_argument('--seg_checkpoint', type=str, default='seg_final.pth')
    parser.add_argument('--gmm_checkpoint', type=str, default='gmm_final.pth')
    parser.add_argument('--alias_checkpoint', type=str, default='alias_final.pth')

    # common
    parser.add_argument('--semantic_nc', type=int, default=13, help='# of human-parsing map classes')
    parser.add_argument('--init_type', choices=['normal', 'xavier', 'xavier_uniform', 'kaiming', 'orthogonal', 'none'], default='xavier')
    parser.add_argument('--init_variance', type=float, default=0.02, help='variance of the initialization distribution')

    # for GMM
    parser.add_argument('--grid_size', type=int, default=5)

    # for ALIASGenerator
    parser.add_argument('--norm_G', type=str, default='spectralaliasinstance')
    parser.add_argument('--ngf', type=int, default=64, help='# of generator filters in the first conv layer')
    parser.add_argument('--num_upsampling_layers', choices=['normal', 'more', 'most'], default='most',
                        help='If \'more\', add upsampling layer between the two middle resnet blocks. '
                             'If \'most\', also add one more (upsampling + resnet) layer at the end of the generator.')

    opt = parser.parse_args()
    return opt


def test(opt, seg, gmm, alias):
    print("Starting test function...")
    up = nn.Upsample(size=(opt.load_height, opt.load_width), mode='bilinear')
    gauss = tgm.image.GaussianBlur((15, 15), (3, 3))
    gauss.cuda()

    test_dataset = VITONDataset(opt)
    if(test_dataset is None or len(test_dataset)==0):
        print("error in loading test_dataset")
    else:
        print("VITONDataset loaded successfully, size:", len(test_dataset))
    test_loader = VITONDataLoader(opt, test_dataset)
    if (test_loader is None):
        print("error in loading test_loader")
    else:
        print("VITONDataloader loaded successfully")

    with torch.no_grad():
        print("Starting generation loop...")
        for i, inputs in enumerate(test_loader.data_loader):
            print(f"\nProcessing batch {i+1}")
            
            try:
                img_names = inputs['img_name']
                c_names = inputs['c_name']['unpaired']
                print("Loaded image names:", img_names)
                print("Loaded cloth names:", c_names)

                img_agnostic = inputs['img_agnostic'].cuda()
                parse_agnostic = inputs['parse_agnostic'].cuda()
                pose = inputs['pose'].cuda()
                c = inputs['cloth']['unpaired'].cuda()
                cm = inputs['cloth-mask']['unpaired'].cuda()
                print("Input tensors loaded to GPU")

                # Part 1. Segmentation generation
                print("Starting segmentation generation...")
                parse_agnostic_down = F.interpolate(parse_agnostic, size=(256, 192), mode='bilinear')
                pose_down = F.interpolate(pose, size=(256, 192), mode='bilinear')
                c_masked_down = F.interpolate(c * cm, size=(256, 192), mode='bilinear')
                cm_down = F.interpolate(cm, size=(256, 192), mode='bilinear')
                seg_input = torch.cat((cm_down, c_masked_down, parse_agnostic_down, pose_down, gen_noise(cm_down.size()).cuda()), dim=1)
                print("Segmentation input shape:", seg_input.shape)

                parse_pred_down = seg(seg_input)
                print("Segmentation prediction completed")

                parse_pred = gauss(up(parse_pred_down))
                parse_pred = parse_pred.argmax(dim=1)[:, None]

                parse_old = torch.zeros(parse_pred.size(0), 13, opt.load_height, opt.load_width, dtype=torch.float).cuda()
                parse_old.scatter_(1, parse_pred, 1.0)

                labels = {
                    0:  ['background',  [0]],
                    1:  ['paste',       [2, 4, 7, 8, 9, 10, 11]],
                    2:  ['upper',       [3]],
                    3:  ['hair',        [1]],
                    4:  ['left_arm',    [5]],
                    5:  ['right_arm',   [6]],
                    6:  ['noise',       [12]]
                }
                parse = torch.zeros(parse_pred.size(0), 7, opt.load_height, opt.load_width, dtype=torch.float).cuda()
                for j in range(len(labels)):
                    for label in labels[j][1]:
                        parse[:, j] += parse_old[:, label]
                print("Parse generation completed")

                # Part 2. Clothes Deformation
                print("Starting clothes deformation...")
                agnostic_gmm = F.interpolate(img_agnostic, size=(256, 192), mode='nearest')
                parse_cloth_gmm = F.interpolate(parse[:, 2:3], size=(256, 192), mode='nearest')
                pose_gmm = F.interpolate(pose, size=(256, 192), mode='nearest')
                c_gmm = F.interpolate(c, size=(256, 192), mode='nearest')
                gmm_input = torch.cat((parse_cloth_gmm, pose_gmm, agnostic_gmm), dim=1)
                print("GMM input shape:", gmm_input.shape)

                _, warped_grid = gmm(gmm_input, c_gmm)
                warped_c = F.grid_sample(c, warped_grid, padding_mode='border', align_corners=True)
                warped_cm = F.grid_sample(cm, warped_grid, padding_mode='border', align_corners=True)
                print("Clothes deformation completed")

                # Part 3. Try-on synthesis
                print("Starting try-on synthesis...")
                misalign_mask = parse[:, 2:3] - warped_cm
                misalign_mask[misalign_mask < 0.0] = 0.0
                parse_div = torch.cat((parse, misalign_mask), dim=1)
                parse_div[:, 2:3] -= misalign_mask

                img_agnostic = F.interpolate(img_agnostic, size=(1024, 768), mode='bilinear', align_corners=False)
                pose = F.interpolate(pose, size=(1024, 768), mode='bilinear', align_corners=False)
                
                alias_input = torch.cat((img_agnostic, pose, warped_c), dim=1)
                print("ALIAS input shapes:")
                print("- alias_input:", alias_input.shape)
                print("- parse:", parse.shape)
                print("- parse_div:", parse_div.shape)
                print("- misalign_mask:", misalign_mask.shape)

                try:
                    output = alias(alias_input, parse, parse_div, misalign_mask)
                    print("ALIAS generation completed successfully")
                except Exception as e:
                    print("Error in ALIAS generation:", str(e))
                    continue

                unpaired_names = []
                for img_name, c_name in zip(img_names, c_names):
                    unpaired_names.append('{}_{}'.format(img_name.split('_')[0], c_name))

                save_path = os.path.join(opt.save_dir, opt.name)
                print(f"Saving output to {save_path}")
                try:
                    save_images(output, unpaired_names, save_path)
                    print("Images saved successfully")
                except Exception as e:
                    print("Error saving images:", str(e))

            except Exception as e:
                print(f"Error processing batch {i+1}:", str(e))
                continue

            if (i + 1) % opt.display_freq == 0:
                print("step: {}".format(i + 1))


def main():
    print("Starting main function...")
    opt = get_opt()
    print("Options loaded")

    save_dir = os.path.join(opt.save_dir, opt.name)
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f"Created save directory: {save_dir}")

    # Initialize models
    print("Initializing models...")
    seg = SegGenerator(opt, input_nc=opt.semantic_nc + 8, output_nc=opt.semantic_nc)
    gmm = GMM(opt, inputA_nc=7, inputB_nc=3)
    opt.semantic_nc = 7
    alias = ALIASGenerator(opt, input_nc=9)
    opt.semantic_nc = 13
    print("Models initialized")

    # Load checkpoints
    print("Loading checkpoints...")
    try:
        seg_path = os.path.join(opt.checkpoint_dir, opt.seg_checkpoint)
        gmm_path = os.path.join(opt.checkpoint_dir, opt.gmm_checkpoint)
        alias_path = os.path.join(opt.checkpoint_dir, opt.alias_checkpoint)
        
        print(f"Loading seg checkpoint from: {seg_path}")
        load_checkpoint(seg, seg_path)
        print(f"Loading gmm checkpoint from: {gmm_path}")
        load_checkpoint(gmm, gmm_path)
        print(f"Loading alias checkpoint from: {alias_path}")
        load_checkpoint(alias, alias_path)
        print("All checkpoints loaded successfully")
    except Exception as e:
        print("Error loading checkpoints:", str(e))
        return

    print("Moving models to GPU...")
    seg.cuda().eval()
    gmm.cuda().eval()
    alias.cuda().eval()
    print("Models ready")

    test(opt, seg, gmm, alias)
    print("finished testing")


if __name__ == '__main__':
    main()