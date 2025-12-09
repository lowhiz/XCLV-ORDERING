from django.db import models
class AdminUser(models.Model):
    """
    Model responsible for storing authentication credentials for 
    administrative staff within the system.

    This model handles the login identity of admin users by storing a unique
    username (admin_id) and the hashed password associated with it. Access 
    control features and admin authentication routines rely on this model.
    """
    
    # The unique identifier used for admin login 
    admin_id = models.CharField(max_length=50, unique=True)
    
    # Stores the hashed version of the password. 
    password = models.CharField(max_length=255)
    
    def __str__(self):
        """
        Returns the unique admin_id for a readable representation of the object.
        """
        return self.admin_id