from django.contrib import admin

from .models import Proposal, ProposalKeyword


@admin.register(ProposalKeyword)
class KeywordAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "official",)
    list_filter = ("official",)


@admin.register(Proposal)
class ProposalAdmin(admin.ModelAdmin):
    exclude = (
        "under_represented_population",
        "under_represented_details",
        "under_represented_other",
    )
    list_display = (
        'number',
        'title',
        'speaker',
        'kind',
        'audience_level',
        'cancelled',
        "date_created",
        "date_last_modified",
    )
    list_display_links = ("title",)
    list_filter = (
        'kind',
        'audience_level',
        'cancelled',
        'recording_release',
    )
    search_fields = ("title", "speaker__name")
    date_hierarchy = "date_created"
