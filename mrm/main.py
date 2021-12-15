import json
import os
import requests
import subprocess
import urllib.parse
from typing import Optional, TypedDict

import typer

app = typer.Typer()


class Session(TypedDict):
    sessionId: str
    sessionKey: str
    sessionToken: str


def assume_session(
    role_arn: str,
    session_name: str,
    external_id: Optional[str],
    mfa_serial: Optional[str],
    mfa_token: Optional[str],
    clean_env: bool = False,
) -> Session:
    cmd = [
        "aws",
        "sts",
        "assume-role",
        f"--role-arn={role_arn}",
        f"--role-session-name={session_name}",
    ]

    if external_id is not None:
        cmd.append(f"--external-id={external_id}")

    if mfa_serial is not None:
        cmd.append(f"--serial-number={mfa_serial}")

    if mfa_token is not None:
        cmd.append(f"--token-code={mfa_token}")

    env = os.environ.copy()
    if clean_env and "AWS_ACCESS_KEY_ID" in env:
        del env["AWS_ACCESS_KEY_ID"]
    if clean_env and "AWS_SECRET_ACCESS_KEY" in env:
        del env["AWS_SECRET_ACCESS_KEY"]
    if clean_env and "AWS_SESSION_TOKEN" in env:
        del env["AWS_SESSION_TOKEN"]

    sts_output = json.loads(subprocess.check_output(cmd, env=env))

    return {
        "sessionId": sts_output["Credentials"]["AccessKeyId"],
        "sessionKey": sts_output["Credentials"]["SecretAccessKey"],
        "sessionToken": sts_output["Credentials"]["SessionToken"],
    }


@app.command()
def web(
    role_arn: str = typer.Option(
        ...,
        help="ARN of the role to assume",
    ),
    session_name: str = typer.Option(
        "MrMSession",
        help="Session name",
    ),
    external_id: str = typer.Option(
        None,
        help="ExternalID",
    ),
    mfa_serial: str = typer.Option(
        None,
        help="Serial number of the MFA device",
    ),
    mfa_token: str = typer.Option(
        None,
        help="MFA token",
    ),
    clean: bool = typer.Option(
        False,
        help="Ignore current AWS_* environment variables when assuming the role"
    )
):
    """Assume a role in the AWS web console"""
    session = assume_session(role_arn, session_name, external_id, mfa_serial, mfa_token, clean)
    encoded_session = urllib.parse.quote_plus(json.dumps(session))
    credentials_url = f"https://signin.aws.amazon.com/federation?Action=getSigninToken&Session={encoded_session}"
    result = requests.get(credentials_url).json()
    destination_console = "https://console.aws.amazon.com/"
    login_url = f"https://signin.aws.amazon.com/federation?Action=login&Destination={destination_console}&SigninToken={result['SigninToken']}"
    typer.secho(f"your login url is:")
    typer.secho(login_url, fg="green")


@app.command()
def shell(
    role_arn: str = typer.Option(
        ...,
        help="ARN of the role to assume",
    ),
    session_name: str = typer.Option(
        "MrMSession",
        help="Session name",
    ),
    external_id: str = typer.Option(
        None,
        help="ExternalID",
    ),
    mfa_serial: str = typer.Option(
        None,
        help="Serial number of the MFA device",
    ),
    mfa_token: str = typer.Option(
        None,
        help="MFA token",
    ),
    clean: bool = typer.Option(
        False,
        help="Ignore current AWS_* environment variables when assuming the role"
    )
):
    session = assume_session(role_arn, session_name, external_id, mfa_serial, mfa_token, clean)
    typer.secho(f"this shell is now setup - no need to run anything else.", fg="green")
    typer.secho(f"when you are done using this session leave the shell with `exit`.", fg="red")
    typer.secho(
        f"to setup another shell run:\nexport AWS_ACCESS_KEY_ID={session['sessionId']}\nexport AWS_SECRET_ACCESS_KEY={session['sessionKey']}\nexport AWS_SESSION_TOKEN={session['sessionToken']}",
        fg="yellow"
    )
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = session["sessionId"]
    env["AWS_SECRET_ACCESS_KEY"] = session["sessionKey"]
    env["AWS_SESSION_TOKEN"] = session["sessionToken"]
    os.execve("/bin/bash", ["/bin/bash"], env)


if __name__ == "__main__":
    app()
