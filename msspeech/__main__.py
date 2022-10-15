"""Entry point."""

import asyncio
import click

try:
    from . import MSSpeech, msspeech_dir, MSSpeechError
except ImportError:
    from msspeech import MSSpeech, msspeech_dir, MSSpeechError


async def a_main(voice_name, text, filename, rate, pitch, volume):
    mss = MSSpeech()
    v = await mss.get_voices_by_substring(voice_name)
    if len(v) == 0:
        raise MSSpeechError("The voice was not found.")
    await mss.set_voice(v[0]['Name'])
    await mss.set_rate(rate)
    await mss.set_pitch(pitch)
    await mss.set_volume(volume)
    await mss.synthesize(text.strip(), filename)

@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument("voice_name")
@click.argument("text")
@click.option("--filename", default="msspeech.mp3", help="Audio file name.")
@click.option("--rate", type=click.IntRange(-100, 100, clamp=True), default=0, help="Speech rate (from -100 to +100 or 0).")
@click.option("--pitch", type=click.IntRange(-100, 100, clamp=True), default=0, help="voice pitch (from -100 to +100 or 0).")
@click.option("--volume", type=click.FloatRange(0.1, 1.0, clamp=True), default=1.0, help="voice volume.")
def main(voice_name, text, filename="msspeech.mp3", rate=0, pitch=0, volume=1.0):
    """Fetch generated tts sounds from msspeech."""
    try:
        click.echo(asyncio.run(a_main(
            voice_name=voice_name,
            text=text,
            filename=filename,
            rate=rate,
            pitch=pitch,
            volume=volume
        )))
    except MSSpeechError as exn:
        click.secho(str(exn), fg='red')
        raise SystemExit(-2)


@click.command()
def update_voices():
    "Delete the file with the list of voices and download the list of voices again"
    import os
    import os.path
    removed = False
    for f in ["voices_list.json", "voices_list_plus.json"]:
        p = os.path.join(msspeech_dir, f)
        if os.path.isfile(p):
            removed = True
            click.echo(f"removing {p}")
            os.remove(p)
    if not removed:
        click.echo("Files not found")
    mss = MSSpeech()
    loop = asyncio.get_event_loop()
    loop.run_until_complete(mss.get_voices_list())

if __name__ == '__main__':
    import sys
    if sys.argv[-1].replace("-", "_").lower() == "update_voices":
        update_voices()
        sys.exit(0)
    main()
