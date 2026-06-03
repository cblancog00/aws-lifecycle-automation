from config import BootstrapConfig


def make_config(**overrides):
    defaults = dict(
        aws_region="eu-west-1",
        aws_account_id="123456789012",
        github_org="myorg",
        github_repo="myrepo",
        environment="dev",
    )
    return BootstrapConfig(**{**defaults, **overrides})


def test_tf_state_bucket_includes_account_and_env():
    cfg = make_config(aws_account_id="111222333444", environment="dev")
    assert cfg.tf_state_bucket == "tfstate-111222333444-dev"


def test_tf_state_bucket_prod():
    cfg = make_config(aws_account_id="111222333444", environment="prod")
    assert cfg.tf_state_bucket == "tfstate-111222333444-prod"


def test_tf_lock_table_includes_env():
    assert make_config(environment="dev").tf_lock_table == "tfstate-lock-dev"
    assert make_config(environment="prod").tf_lock_table == "tfstate-lock-prod"


def test_terraform_role_name():
    cfg = make_config(environment="dev")
    assert cfg.terraform_role_name == "github-actions-terraform-dev"


def test_oidc_provider_url():
    cfg = make_config()
    assert cfg.oidc_provider_url == "https://token.actions.githubusercontent.com"


def test_oidc_provider_arn_contains_account():
    cfg = make_config(aws_account_id="111222333444")
    assert (
        cfg.oidc_provider_arn
        == "arn:aws:iam::111222333444:oidc-provider/token.actions.githubusercontent.com"
    )


def test_github_subject():
    cfg = make_config(github_org="myorg", github_repo="myrepo")
    assert cfg.github_subject == "repo:myorg/myrepo:*"
