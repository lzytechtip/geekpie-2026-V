import argparse
import json
from pathlib import Path

from protocol import check_submission


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('signature', type=Path, help='JSON with lowercase hex R and s')
    parser.add_argument('--public-key', required=True, help='public_key from the verification service')
    parser.add_argument('--message', required=True, help='exact target_message from the verification service')
    args = parser.parse_args()
    try:
        challenge = dict(public_key=args.public_key, target_message=args.message)
        submission = json.loads(args.signature.read_text(encoding='utf-8'))
        valid = check_submission(challenge, submission)
    except (OSError, ValueError):
        valid = False
    print('VALID' if valid else 'INVALID')
    raise SystemExit(0 if valid else 1)
