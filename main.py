import argparse
import hashlib
import os

from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes


def encrypt_file(file, key, output):
    # 如果output路径不存在，则逐级创建
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    if len(key) not in (16, 24, 32):
        raise ValueError('Key must be 16, 24, or 32 bytes long')
    with open(file, 'rb') as f_in, open(output, 'wb') as f_out:
        while True:
            chunk = f_in.read(64 * 1024)  # Read in chunks of 64*1024 bytes
            if len(chunk) == 0:
                break  # End of file
            nonce = get_random_bytes(8)
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            ciphertext = cipher.encrypt(chunk)
            f_out.write(nonce + ciphertext)  # Write nonce and ciphertext to output file


def decrypt_file(file, key, output):
    # 如果output路径不存在，则逐级创建
    if not os.path.exists(os.path.dirname(output)):
        os.makedirs(os.path.dirname(output))
    if len(key) not in (16, 24, 32):
        raise ValueError('Key must be 16, 24, or 32 bytes long')
    with open(file, 'rb') as f_in, open(output, 'wb') as f_out:
        while True:
            chunk = f_in.read(64 * 1024 + 8)  # Read in chunks of 64*1024 bytes + 8 bytes nonce
            if len(chunk) == 0:
                break  # End of file
            nonce = chunk[:8]
            ciphertext = chunk[8:]
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
            plaintext = cipher.decrypt(ciphertext)
            f_out.write(plaintext)


def enc(f_input, f_output, key):
    if f_input['isfile']:
        encrypt_file(f_input['path'], key, f_output['path'])
    else:
        def walk_dir(path, outpath):
            # 逐层递归遍历文件夹
            for root, dirs, files in os.walk(path):
                for file in files:
                    # file拓展名添加.enc
                    encrypt_file(os.path.join(root, file), key, os.path.join(outpath, file + '.enc'))
                for _dir in dirs:
                    walk_dir(os.path.join(root, _dir), os.path.join(outpath, _dir))
        walk_dir(f_input['path'], f_output['path'])


def dec(f_input, f_output, key):
    if f_input['isfile']:
        decrypt_file(f_input['path'], key, f_output['path'])
    else:
        # 逐层递归遍历文件夹
        def walk_dir(path, outpath):
            for root, dirs, files in os.walk(path):
                for file in files:
                    if file.endswith('.enc'):
                        decrypt_file(os.path.join(root, file), key, os.path.join(outpath, file[:-4]))
                for _dir in dirs:
                    walk_dir(os.path.join(root, _dir), os.path.join(outpath, _dir))
        walk_dir(f_input['path'], f_output['path'])


def varg():
    parser = argparse.ArgumentParser(description='Protect your documents')
    subparsers = parser.add_subparsers(dest='command', help='sub-command help')

    # 加密文件
    encrypt_parser = subparsers.add_parser('encrypt', help='encrypt help')
    encrypt_parser.add_argument('--file', '-f', help='file to encrypt', default=None)
    encrypt_parser.add_argument('--key', '-k', help='key to encrypt with', default=None)
    encrypt_parser.add_argument('--output', '-o', help='output file', default=None)
    encrypt_parser.add_argument('--path', '-p', help='path to encrypt', default=None)
    encrypt_parser.add_argument('--outpath', '-op', help='output path', default=None)
    # 解密文件
    decrypt_parser = subparsers.add_parser('decrypt', help='decrypt help')
    decrypt_parser.add_argument('--file', '-f', help='file to decrypt', default=None)
    decrypt_parser.add_argument('--key', '-k', help='key to decrypt with', default=None)
    decrypt_parser.add_argument('--output', '-o', help='output file', default=None)
    decrypt_parser.add_argument('--path', '-p', help='path to decrypt', default=None)
    decrypt_parser.add_argument('--outpath', '-op', help='output path', default=None)
    args = parser.parse_args()
    return args


def main():
    def hash_key(_key: bytes) -> bytes:
        return hashlib.sha256(_key).digest()
    args = varg()
    if not args.command:
        print('No command given')
        return
    if not args.key:
        # 加载本地密钥
        key_path = os.path.join(os.getcwd(), 'key.aes')
        # 如果没有或者为空，生成一个
        if not os.path.exists(key_path) or os.path.getsize(key_path) == 0:
            with open(key_path, 'wb') as f:
                f.write(get_random_bytes(32))

        # 赋值给key
        with open(key_path, 'rb') as f:
            key: bytes = hash_key(f.read())
    else:
        key: bytes = hash_key(args.key.encode('utf-8'))

    # 获取是否是文件还是文件夹/文件参数存在则为文件
    f_input, f_output = {'isfile': True, 'path': ''}, {'isfile': True, 'path': ''}
    if args.file:
        f_input['path'] = os.path.abspath(args.file)
    else:
        f_input['isfile'] = False
        f_input['path'] = os.path.abspath(args.path)
    if args.output:
        f_output['path'] = os.path.abspath(args.output)
    else:
        f_output['isfile'] = False
        f_output['path'] = os.path.abspath(args.outpath)
    if not f_input['path']:
        print('No input file given')
        return
    if not f_output['path']:
        print('No output file given')
        return
    if not f_input['isfile'] and f_output['isfile']:
        print('Input is a directory, but output is a file')
        return

    if args.command == 'encrypt':
        enc(f_input, f_output, key)
    elif args.command == 'decrypt':
        dec(f_input, f_output, key)
    else:
        print('No command given')
        return


if __name__ == '__main__':
    main()
