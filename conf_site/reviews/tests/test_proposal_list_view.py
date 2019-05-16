# -*- coding: utf-8 -*-
from random import randint
from django.urls import reverse

from symposion.proposals.models import ProposalKind
from symposion.schedule.tests.factories import SectionFactory

from conf_site.accounts.tests import AccountsTestCase
from conf_site.proposals.tests.factories import ProposalFactory
from conf_site.reviews.models import ProposalResult
from conf_site.reviews.tests import ReviewingTestCase


class ProposalListViewTestCase(ReviewingTestCase, AccountsTestCase):
    reverse_view_name = "review_proposal_list"

    def test_no_cancelled_proposals(self):
        """Verify that cancelled proposals do not appear in proposal list."""
        VALID_PROPOSAL_COUNT = 4
        INVALID_PROPOSAL_COUNT = 3

        # Create proposals.
        valid_proposals = ProposalFactory.create_batch(
            size=VALID_PROPOSAL_COUNT, cancelled=False
        )
        invalid_proposals = ProposalFactory.create_batch(
            size=INVALID_PROPOSAL_COUNT, cancelled=True
        )

        # User must be in the reviewers group in order to access
        # this view.
        self._add_to_reviewers_group()
        response = self.client.get(
            reverse(self.reverse_view_name, args=self.reverse_view_args)
        )
        for valid_proposal in valid_proposals:
            self.assertContains(response, valid_proposal.title)
        for invalid_proposal in invalid_proposals:
            self.assertNotContains(response, invalid_proposal.title)

    def test_proposal_count(self):
        """Verify that proposal list contains count of proposals."""
        self._add_to_reviewers_group()
        # Setup the ProposalKinds for talks and tutorials.
        section = SectionFactory()
        talk_kind = ProposalKind.objects.create(
            section=section, name="Talk", slug="talk"
        )
        tutorial_kind = ProposalKind.objects.create(
            section=section, name="Tutorial", slug="tutorial"
        )
        # Create a random number of talks and tutorials.
        num_talks = randint(2, 10)
        num_tutorials = randint(2, 10)
        num_total_proposals = num_talks + num_tutorials
        ProposalFactory.create_batch(size=num_talks, kind=talk_kind)
        ProposalFactory.create_batch(size=num_tutorials, kind=tutorial_kind)

        response = self.client.get(
            reverse(self.reverse_view_name, args=self.reverse_view_args)
        )
        self.assertContains(
            response,
            "<strong>{}</strong> proposals".format(num_total_proposals),
        )
        self.assertContains(
            response, "<strong>{}</strong> talks".format(num_talks)
        )
        self.assertContains(
            response, "<strong>{}</strong> tutorials".format(num_tutorials)
        )

    def test_changing_proposal_status(self):
        self._become_superuser(self.user)
        # Create multiple proposals.
        num_proposals = randint(3, 6)
        proposals = ProposalFactory.create_batch(size=num_proposals)
        for result_status in ProposalResult.RESULT_STATUSES:
            # Use post data to change the first three proposals' statuses.
            post_data = {
                "proposal_pks": [1, 2, 3],
                "mark_status": result_status[0],
            }
            response = self.client.post(reverse("review_multiedit"), post_data)
            # Verify that we are redirected to the correct page
            # (a list of proposals with the same changed status).
            self.assertRedirects(
                response,
                reverse(
                    "review_proposal_result_list", args=[result_status[0]]
                ),
            )
            # Verify that status has changed and all other proposals
            # have remained the same.
            for proposal in proposals:
                if proposal.pk in post_data["proposal_pks"]:
                    self.assertEqual(
                        proposal.review_result.status, result_status["0"]
                    )
                else:
                    self.assertEqual(
                        proposal.review_result.status,
                        ProposalResult.RESULT_UNDECIDED,
                    )
