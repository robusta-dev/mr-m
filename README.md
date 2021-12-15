# Intro

Need to easily assume AWS IAM roles? Mr. M has your back!

Features:

1. Assume IAM roles
2. Spawn a bash shell with preconfigured environment variables for the new role
3. Open the AWS web console for an assumed role
4. Supports cross-account roles
5. Supports multi-factor authentication


# Usage
Installation:
```
pip install git+https://github.com/robusta-dev/mr-m
```

Assume a role and open a preconfigured bash-shell:
```
mr-m shell \
     --clean \
     --role-arn="arn:aws:iam::RoleGoesHere" \
     --external-id="external-id-goes-here" \
     --mfa-serial="arn:aws:iam::mfa-arn-goes-here" \
     --mfa-token=<MFA_TOKEN>
```

Assume a role and generate a link for logging in to the AWS Web Console with that role
```
mr-m web \
     --role-arn="arn:aws:iam::RoleGoesHere" \
     --external-id="external-id-goes-here" \
     --mfa-serial="arn:aws:iam::mfa-arn-goes-here" \
     --mfa-token=<MFA_TOKEN>
```

# FAQ
## What's up with the name?
When I was in fifth grade I had a teacher named Mr. M. He was a wonderful teacher, but all I remember from his classes is one sentence he said often:

	You should never assume, because when you assume you make an ASS of U and ME. 

I assume that Mr. M taught me many other things, but this is all I remember from fifth grade.

