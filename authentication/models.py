from __future__ import unicode_literals

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
import json

# class Corpus(models.Model):
#     name = models.CharField('name', max_length=30)
#     c_id = models.IntegerField('c_id')
#     parent = models.ForeignKey('self', blank=True, null=True, related_name='children', verbose_name='parent')
#     deep_level = models.IntegerField('depth', default=0)
#     def __str__(self):
#         return self.name

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    corpus_id = models.CharField(max_length=1000,default=json.dumps([0]*1000))

    def setid(self, x):
        self.corpus_id = json.dumps(x)
    
    def getid(self):
        if isinstance(self.corpus_id,(int)):
            temp=[0]*1000
            checked=[tree_first[self.corpus_id]]+tree_second[self.corpus_id]
            for i in checked:
                temp[i]=1
            self.corpus_id=json.dumps(temp)
            self.save()
            return temp
        return json.loads(self.corpus_id)
    @staticmethod
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            UserProfile(user=instance).save()

post_save.connect(UserProfile.create_user_profile, sender=User)
       

tree_first=[0, 2, 51, 74, 99, 145, 179, 208, 237, 280, 299]
tree_second=[[1], [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50], [52, 53, 54, 55, 56, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73], [75, 76, 77, 78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98], [100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114, 115, 116, 117, 118, 119, 120, 121, 122, 123, 124, 125, 126, 127, 128, 129, 130, 131, 132, 133, 134, 135, 136, 137, 138, 139, 140, 141, 142, 143, 144], [146, 147, 148, 149, 150, 151, 152, 153, 154, 155, 156, 157, 158, 159, 160, 161, 162, 163, 164, 165, 166, 167, 168, 169, 170, 171, 172, 173, 174, 175, 176, 177, 178], [180, 181, 182, 183, 184, 185, 186, 187, 188, 189, 190, 191, 192, 193, 194, 195, 196, 197, 198, 199, 200, 201, 202, 203, 204, 205, 206, 207], [209, 210, 211, 212, 213, 214, 215, 216, 217, 218, 219, 220, 221, 222, 223, 224, 225, 226, 227, 228, 229, 230, 231, 232, 233, 234, 235, 236], [238, 239, 240, 241, 242, 243, 244, 245, 246, 247, 248, 249, 250, 251, 252, 253, 254, 255, 256, 257, 258, 259, 260, 261, 262, 263, 264, 265, 266, 267, 268, 269, 270, 271, 272, 273, 274, 275, 276, 277, 278, 279], [281, 282, 283, 284, 285, 286, 287, 288, 289, 290, 291, 292, 293, 294, 295, 296, 297, 298], [300, 301, 302, 303, 304, 305, 306, 307, 308, 309, 310, 311, 312, 313, 314, 315, 316, 317, 318, 319, 320]]