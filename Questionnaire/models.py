from django.db import models


class Question(models.Model):
    type_choices = (
        ('single_choice', '单选题'),
        ('multiple_choice', '多选题'),
        ('fill_in_the_blanks', '填空题'),
        ('true_or_false', '判断题'),
        ('question_and_answer', '问答题'),
    )

    id = models.AutoField(primary_key=True, verbose_name='id')
    type = models.CharField(max_length=50, choices=type_choices, verbose_name='类型')
    content = models.TextField(max_length=1600, verbose_name='题目')
    note = models.TextField(max_length=1600, verbose_name='说明')


class Questionnaire(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')
    title = models.TextField(max_length=40, verbose_name='标题')
    introduction = models.TextField(max_length=100, verbose_name='简介')


class Report(models.Model):
    id = models.AutoField(primary_key=True, verbose_name='id')

