# Generated by Django 2.0.13 on 2019-05-13 22:09

from django.db import migrations


def migrate_messages_to_feedback(apps, schema_editor):
    """
    Migrate symposion.reviews.models.ProposalMessage to
    conf_site.reviews.models.ProposalFeedback.
    """
    ProposalMessage = apps.get_model("symposion_reviews", "ProposalMessage")
    ProposalFeedback = apps.get_model("reviews", "ProposalFeedback")
    # There are unlikely to be so many ProposalMessage objects
    # that it would make sense to use `.iterator()` here.
    for message in ProposalMessage.objects.all():
        ProposalFeedback.objects.create(
            proposal=message.proposal.proposal,
            author=message.user,
            comment=message.message,
            comment_html=message.message_html,
        )




class Migration(migrations.Migration):

    dependencies = [("symposion_reviews", "0001_initial")]

    operations = [migrations.RunPython(migrate_messages_to_feedback)]