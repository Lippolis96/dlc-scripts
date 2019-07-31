# videos.py
import argparse

parser = argparse.ArgumentParser(description='Videos to images')
parser.add_argument('--mytype', type=str, default="cat", help='Type of data')
args = parser.parse_args()

print(args.mytype)
