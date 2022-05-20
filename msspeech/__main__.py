"""Entry point."""

import asyncio
import click

from . import MSSpeech, MSSpeechError


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
@click.option("--rate", default=0, help="Speech rate (from -100 to +100 or 0).")
@click.option("--pitch", default=0, help="voice pitch (from -100 to +100 or 0).")
@click.option("--volume", default=1.0, help="voice volume.")
def main(voice_name, text, filename="msspeech.mp3", rate=0, pitch=0, volume=1.0):
    """Fetch generated tts sounds from msspeech."""
    try:
        loop = asyncio.get_event_loop()
        click.echo(loop.run_until_complete(a_main(
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


if __name__ == '__main__':
    main()
