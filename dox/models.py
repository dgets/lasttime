from django.db import models


class MainHelpTopic(models.Model):
    """
    Holds information relevant to each particular main help topic within the
    dox view here.  Topics relevant only to a particular view for a particular
    case will be held in a different model.
    """

    name = models.CharField(max_length=25)
    heading = models.CharField(max_length=40)


class MainHelpTopicDetail(models.Model):
    """
    Holds information specific to a single topic above.
    """

    topic = models.ForeignKey(MainHelpTopic, on_delete=models.CASCADE)
    sub_topic = models.CharField(max_length=80)
    text = models.TextField()


class SpecificViewHelpTopic(models.Model):
    """
    Holds information to be pulled from a specific view for help on a
    specific aspect thereof.
    """

    name = models.CharField(max_length=25)
    view = models.CharField(max_length=40, default="")
    heading = models.CharField(max_length=40)


class SpecificViewTopicDetail(models.Model):
    """
    Holds sub-information specific to a single topic above.
    """

    topic = models.ForeignKey(SpecificViewHelpTopic, on_delete=models.CASCADE)
    sub_topic = models.CharField(max_length=80)
    text = models.TextField()
