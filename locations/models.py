from django.db import models

class City(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    cover_image = models.ImageField(upload_to='cities/', blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'Cities'

class Place(models.Model):
    city = models.ForeignKey(City, on_delete=models.CASCADE, related_name='places')
    name = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.city.name})"

class PlaceImage(models.Model):
    place = models.ForeignKey(Place, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='places/')

    def __str__(self):
        return f"Image for {self.place.name}"
