from rest_framework.decorators import action
from rest_framework.response import Response
from django.conf import settings
from apps.cart.models import Cart
from apps.cart.cart import Cart as cart_session

CART_SESSION_ID = settings.CART_SESSION_ID
class ImageMixin:
    """
    Mixin providing reusable image upload and deletion actions
    for viewsets.

    This mixin is designed to simplify image management for models
    that have related image objects. It supports dynamic serializer
    and foreign key configuration, making it reusable across multiple
    resources such as products, variants, categories, or profiles.

    Attributes:
        image_serializer_class (ModelSerializer):
            Serializer class used for validating and serializing
            image objects.

        image_related_name (str):
            Name of the related image manager on the parent object.
            Defaults to 'images'.

        image_fk_field (str):
            Name of the foreign key field linking the image model
            to the parent object. This attribute must be defined
            in child classes using the mixin.
    """
    image_serializer_class = None
    image_related_name = 'images'  

    @action(
        detail=True, 
        methods=['post'], 
        url_path='images/upload'
    )
    def upload_image(self, request, *args, **kwargs):
        """
        Upload and attach an image to the current object.

        Validates incoming image data using the configured
        serializer class and saves the image while dynamically
        assigning the related parent object.

        Args:
            request (Request):
                Incoming HTTP request containing image data.
            *args:
                Additional positional arguments.
            **kwargs:
                Additional keyword arguments.

        Returns:
            Response:
                - 201 Created with serialized image data if upload succeeds.
                - 400 Bad Request if validation fails.
        """
        obj = self.get_object()
        serializer = self.image_serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save(**{self.image_fk_field: obj})  # dynamic FK
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(
        detail=True, 
        methods=['delete'], 
        url_path='images/delete/(?P<image_id>[^/.]+)'
    )
    def delete_image(self, request, pk=None, image_id=None):
        """
        Delete an image associated with the current object.

        Retrieves the target image using its identifier and
        dynamically filters it against the related parent object
        before deletion.

        Args:
            request (Request):
                Incoming HTTP request.
            pk (str | int, optional):
                Primary key of the parent object.
            image_id (str | int, optional):
                Identifier of the image to delete.

        Returns:
            Response:
                - 204 No Content if deletion succeeds.
                - 404 Not Found if the image does not exist.
        """
        obj = self.get_object()
        image_model = self.image_serializer_class.Meta.model
        try:
            image = image_model.objects.get(id=image_id, **{self.image_fk_field: obj})
            image.delete()
            return Response({"message": "Image deleted"}, status=204)
        except image_model.DoesNotExist:
            return Response({"error": "Image not found"}, status=404)
        
class CartMixin:
    def _get_cart(self, request):
        db_cart, _ = Cart.objects.get_or_create(user=request.user)
        fake_session = {CART_SESSION_ID: db_cart.items}
        cart = cart_session(fake_session)
        return cart, db_cart, fake_session

    def _save_cart(self, db_cart : Cart, cart_dict : cart_session):
        db_cart.items = cart_dict
        db_cart.save()
