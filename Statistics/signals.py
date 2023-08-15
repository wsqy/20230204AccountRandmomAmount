# import datetime
# from django.dispatch import receiver
# from django.db.models.signals import post_save

# from Statistics.models import DayBuyer, DaySeller, MouthBuyer, MouthSeller

# from Tran.models import Transaction


# @receiver(post_save, sender=Transaction)
# def transaction_create(sender, instance=None, created=False, **kwargs):
#     if created:
#         print('1111111111\n'*5)
#         daybuyer = DayBuyer.objects.get_or_create(buyer=instance.buyer, date=instance.date)[0]
#         daybuyer.amount_total += instance.amount
#         daybuyer.save()

#         dayseller = DaySeller.objects.get_or_create(seller=instance.seller, date=instance.date)[0]
#         dayseller.amount_total += instance.amount
#         dayseller.save()

#         mouthbuyer = DaySeller.objects.get_or_create(buyer=instance.buyer, date=instance.date.strftime("%Y%m"))[0]
#         mouthbuyer.amount_total += instance.amount
#         mouthbuyer.save()

#         mouthseller = DaySeller.objects.get_or_create(seller=buyer, date=instance.date.strftime("%Y%m"))[0]
#         mouthseller.amount_total += instance.amount
#         mouthseller.save()