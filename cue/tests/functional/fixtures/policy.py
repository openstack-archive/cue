import fixtures

from cue.common import policy


class PolicyFixture(fixtures.Fixture):
    def setUp(self):
        policy.init()
        super(PolicyFixture, self).setUp()
        self.addCleanup(policy.reset)
