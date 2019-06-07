import bcrypt
import click
import sys


@click.group()
def cli():
    pass


@click.command('hash')
@click.option('--cost', '-c', default=10, type=click.INT,
              help='cost of hashing (number of iterations of bcrypt function == 2^cost)')
@click.option('--version', '-v', default='2a', type=click.Choice(["2a", "2b"]), help='bcrypt hash version')
@click.argument('password', nargs=1)
def hash_password(cost, version, password):
    hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(prefix=bytes(version, 'utf-8')
, rounds=cost))
    click.echo(hashed_password.decode('utf-8'))


@click.command('match')
@click.argument('password', nargs=1)
@click.argument('hashed_password', nargs=1)
def match_password(password, hashed_password):
    if bcrypt.checkpw(password.encode('utf-8'), hashed_password.encode('utf-8')):
        print("SUCCESS Password matches to provided hash and salt")
    else:
        print("FAILURE Password doesn't match to provided hash and salt")
        sys.exit(2)


cli.add_command(hash_password)
cli.add_command(match_password)
