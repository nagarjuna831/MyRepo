from django.core.management.base import BaseCommand
from subscription.models import SubscriptionModel
from subscription.serializers import SubscriptionSerializer
from django.db.utils import IntegrityError

class Command(BaseCommand):
    help = 'Create Subscription table'
    names = ['Free', 'Deluxe', 'Ultimate', 'Custom']
    monthly_amounts = [0, 100, 200, 300]
    yearly_amounts = [0, 1000, 2000, 3000]
    form_counts = [5, 50, 100, 200]
    team_counts = [1, 10, 20, 40]
    workflow_counts = [1, 30, 60, 90]
    email_counts = [50, 400, 800, 1000]
    custome_form_counts = ['Y','Y','Y','Y']
    e_signature_counts = ['Y','Y','Y','Y']
    space_assign = ['100', '1000', '2000', '3000']
    monthly_submission = [10, 20, 40, 60]
    subscriptions = []
    for i in range(4):
        subscription = {}
        subscription['name'] = names[i]
        subscription['monthly_amount'] = monthly_amounts[i]
        subscription['yearly_amount'] = yearly_amounts[i]
        subscription['form_count'] = form_counts[i]
        subscription['team_count'] = team_counts[i]
        subscription['workflow_count'] = workflow_counts[i]
        subscription['email_count'] = email_counts[i]
        subscription['custome_form_count'] = custome_form_counts[i]
        subscription['e_signature_count'] = e_signature_counts[i]
        subscription['space_assign'] = space_assign[i]
        subscription['monthly_submission'] = monthly_submission[i]
        subscriptions.append(subscription)

    def handle(self, *args, **options):
        try:
            SubscriptionModel.objects.all().delete()
            for i in range(4):
                my_objects = SubscriptionModel.objects.create(**self.subscriptions[i])
                my_objects.save()
            print("Subscription table successfully  created!")
        except IntegrityError as e:
            print(e)
        except Exception as e:
            print(e)