from config import BootstrapConfig
from iam import _build_permission_policy, _build_trust_policy


def make_config():
    return BootstrapConfig(
        aws_region="eu-west-1",
        aws_account_id="123456789012",
        github_org="myorg",
        github_repo="myrepo",
        environment="dev",
    )


class TestTrustPolicy:
    def test_principal_is_oidc_provider(self):
        cfg = make_config()
        policy = _build_trust_policy(cfg)
        stmt = policy["Statement"][0]
        assert stmt["Principal"]["Federated"] == cfg.oidc_provider_arn

    def test_action_is_assume_role_with_web_identity(self):
        policy = _build_trust_policy(make_config())
        assert policy["Statement"][0]["Action"] == "sts:AssumeRoleWithWebIdentity"

    def test_subject_condition_matches_github_subject(self):
        cfg = make_config()
        policy = _build_trust_policy(cfg)
        condition = policy["Statement"][0]["Condition"]["StringLike"]
        assert condition["token.actions.githubusercontent.com:sub"] == cfg.github_subject

    def test_audience_condition_is_sts(self):
        policy = _build_trust_policy(make_config())
        condition = policy["Statement"][0]["Condition"]["StringEquals"]
        assert condition["token.actions.githubusercontent.com:aud"] == "sts.amazonaws.com"


class TestPermissionPolicy:
    def test_required_sids_present(self):
        cfg = make_config()
        policy = _build_permission_policy(cfg)
        sids = {s["Sid"] for s in policy["Statement"]}
        assert "TerraformStateAccess" in sids
        assert "TerraformStateLock" in sids
        assert "LambdaManagement" in sids
        assert "IAMPassRoleToLambda" in sids
        assert "STSCallerIdentity" in sids

    def test_state_bucket_arn_in_resources(self):
        cfg = make_config()
        policy = _build_permission_policy(cfg)
        stmt = next(s for s in policy["Statement"] if s["Sid"] == "TerraformStateAccess")
        assert f"arn:aws:s3:::{cfg.tf_state_bucket}" in stmt["Resource"]
        assert f"arn:aws:s3:::{cfg.tf_state_bucket}/*" in stmt["Resource"]

    def test_lock_table_arn_in_resources(self):
        cfg = make_config()
        policy = _build_permission_policy(cfg)
        stmt = next(s for s in policy["Statement"] if s["Sid"] == "TerraformStateLock")
        assert cfg.tf_lock_table in stmt["Resource"]

    def test_iam_pass_role_scoped_to_lambda(self):
        cfg = make_config()
        policy = _build_permission_policy(cfg)
        stmt = next(s for s in policy["Statement"] if s["Sid"] == "IAMPassRoleToLambda")
        condition = stmt["Condition"]["StringEquals"]
        assert condition["iam:PassedToService"] == "lambda.amazonaws.com"

    def test_environment_scoped_in_resource_arns(self):
        cfg = make_config()
        policy = _build_permission_policy(cfg)
        sqs_stmt = next(s for s in policy["Statement"] if s["Sid"] == "SQSManagement")
        assert "-dev-" in sqs_stmt["Resource"]
