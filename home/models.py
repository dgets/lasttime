from django.db import models


class NavInfo(models.Model):
    """
    Holds the navbar information.
    """

    link = models.CharField(max_length=20)
    link_text = models.CharField(max_length=20)

    def __str__(self):
        return link + " with text " + link_text


class HeaderInfo(models.Model):
    """
    Holds the header text.
    """

    motto = models.CharField(max_length=40)
    mission = models.CharField(max_length=180)

    def __str__(self):
        return motto + ": " + mission
