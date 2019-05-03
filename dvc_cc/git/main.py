from argparse import ArgumentParser
#from dvc_cc.git.main_core import *

DESCRIPTION = 'Git-Helper to commit and push all changes to the git repro of the current branch or create a new branch from the current master'

def main():

    parser = ArgumentParser(description = DESCRIPTION)
    parser.add_argument(
        'slide', action='store', type=str, metavar='SLIDEFILE',
        help='Path to SLIDEFILE in  OpenSlide tif format.'
    )
    parser.add_argument(
        '--desc', action='store', type=str, metavar='XMLFILE', default=None,
        help='Path to MASKFILE in CAMELYON XML format. If this is not given it will done a simple tissue segmentation with an otsu algorithm.'
    )

    parser.add_argument('--pixel-spacing', nargs='+', type=float,default=[0.0002439,0.00048781,0.00097561], help='The pixel spacing that you want to use to get the HDF5-File. A lower number means a higher resolution. In CAMEYLON16 the first scanner have the following values: [0.0002439 0.00048781 0.00097561 0.00195122 0.00390244 0.00780488 0.0156098 0.0312195 0.062439 0.124878] and the second scanner: [0.00022727 0.00045454 0.00090909 0.00181818 0.00363636 0.00727273 0.0145455 0.0290909 0.0581818], If you want two layers at the highest resolution good values would be 0.0002439 and 0.00048781.')

    # Todo:
    # parser.add_argument('--no_mask_to_save', dest='save_mask', action='store_false')
    # parser.set_defaults(save_mask=True)

    parser.add_argument(
        '--intervall-to-push-to-hdf5', action='store', type=int, default=100,
        help='The intervall that is used to push the samples to the hdf5-file. If this number is really large, than you need more RAM but it could decrese the computation speed.'
    )

    parser.add_argument(
        '--output', action='store', type=str, default='tiles.hdf5',
        help='Path and name of the HDF-5-File to save. Default: tiles.hdf5'
    )

    parser.add_argument(
        '--tilesize', action='store', type=int, default=512,
        help='the size of the tile in the HDF-File. Default 512, means that each tile has 512x512 pixels.'
    )

    parser.add_argument(
        '--stepsize', action='store', type=int, default=512,
        help='The stepsize that is used to calculate the next position. If the stepsize is smaller than the tilesize the tiles will overlap. Default the stepsize = tilesize => no overlapping'
    )

    parser.add_argument(
        '--run-on-testmode', action='store_true',default=False,
        help='If you run at on the testmode only 5 epochs will be saved.'
    )

    args = parser.parse_args()
