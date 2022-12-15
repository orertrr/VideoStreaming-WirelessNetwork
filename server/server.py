import click

@click.command()
@click.option("-p", "--port", default = 10000, help = "Server port")
@click.option("-v", "--video", default = "camera", help = "Video source: filename or camera")
def main(port, video):
    print(f"Server port: {port}")
    print(f"Video: {video}")

if __name__ == "__main__":
    main()