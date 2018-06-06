from django.db import models


class BlackPhone(models.Model):
    phone = models.CharField(max_length=128)

    def __str__(self):
        return '{}'.format(self.phone)


class CityGroup(models.Model):
    name = models.CharField(max_length=128)
    whois_code = models.CharField(max_length=128)

    def __str__(self):
        return '{}'.format(self.name)


class City(models.Model):
    name = models.CharField(max_length=128)
    name_for_select = models.CharField(max_length=128)
    taxi_phone = models.CharField(max_length=128)
    phone_code = models.IntegerField()
    phone_length_without_code = models.IntegerField()
    from_address_check = models.BooleanField()
    to_address_check = models.BooleanField()
    # city_group = models.ForeignKey(CityGroup)
    tarif = models.IntegerField(blank=True, null=True)
    group_id = models.IntegerField()
    city_center_lat = models.FloatField()
    city_center_lng = models.FloatField()
    city_zoom = models.IntegerField()
    # main_in_group = models.BooleanField()
    day_brigadier_phone = models.CharField(
        max_length=128, blank=True, null=True)
    night_brigadier_phone = models.CharField(
        max_length=128, blank=True, null=True)
    email = models.CharField(max_length=128, blank=True, null=True)

    def __str__(self):
        return '{}'.format(self.name)
