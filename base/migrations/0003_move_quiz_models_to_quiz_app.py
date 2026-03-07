from django.db import migrations


class Migration(migrations.Migration):
    dependencies = [
        ('quiz', '0001_initial'),
        ('base', '0002_quiz_models_and_seed_data'),
    ]

    operations = [
        migrations.SeparateDatabaseAndState(
            database_operations=[],
            state_operations=[
                migrations.RemoveField(
                    model_name='quiz',
                    name='category',
                ),
                migrations.RemoveField(
                    model_name='quizquestion',
                    name='quiz',
                ),
                migrations.DeleteModel(
                    name='MultiplayerSession',
                ),
                migrations.DeleteModel(
                    name='QuizCategory',
                ),
                migrations.DeleteModel(
                    name='Quiz',
                ),
                migrations.DeleteModel(
                    name='QuizQuestion',
                ),
            ],
        ),
    ]
