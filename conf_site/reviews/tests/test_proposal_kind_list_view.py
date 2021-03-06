from random import randint

from django.urls import reverse

from faker import Faker

from conf_site.accounts.tests import AccountsTestCase
from conf_site.proposals.tests.factories import (
    ProposalFactory,
    ProposalKindFactory,
)
from conf_site.reviews.tests import ReviewingTestCase


class ProposalKindListViewTestCase(ReviewingTestCase, AccountsTestCase):
    reverse_view_name = "review_proposal_kind_list"

    def setUp(self):
        super().setUp()
        self.faker = Faker()

        self.proposal_kind = ProposalKindFactory.create()
        self.reverse_view_args = [self.proposal_kind.slug]

    # Disable reviewing methods that are not valid for this view
    # because it contains a subset of all proposals.
    def test_blind_reviewing_types_as_reviewer(self):
        pass

    def test_blind_reviewers_as_superuser(self):
        pass

    def test_invalid_kind(self):
        """Verify that a random kind returns a 404."""
        self._add_to_reviewers_group()
        response = self.client.get(
            reverse(self.reverse_view_name, args=[self.faker.word()])
        )
        self.assertEqual(response.status_code, 404)

    def test_correct_information(self):
        """Verify that shown proposals are correct."""
        self._add_to_reviewers_group()
        shown_proposals = ProposalFactory.create_batch(
            size=randint(5, 10), kind=self.proposal_kind
        )
        unshown_proposals = ProposalFactory.create_batch(size=randint(5, 10))

        response = self.client.get(
            reverse(self.reverse_view_name, args=self.reverse_view_args)
        )
        for proposal in shown_proposals:
            self.assertContains(response, proposal.title)
        for proposal in unshown_proposals:
            self.assertNotContains(response, proposal.title)
