from decimal import Decimal

from django.conf import settings

from carton import module_loading
from carton import settings as carton_settings
from calbase.models import Equipment


class CartItem(object):
    """
    A cart item, with the associated product, its quantity and its price.
    """
    def __init__(self, equipment):
        self.equipment = equipment

    def __repr__(self):
        return u'CartItem Object (%s)' % self.equipment

    def to_dict(self):
        return {
            'equipment_pk': self.equipment.pk,
        }



class Cart(object):

    """
    A cart that lives in the session.
    """
    def __init__(self, session, session_key=None):
        self._items_dict = {}
        self.session = session
        self.session_key = session_key or carton_settings.CART_SESSION_KEY
            # If a cart representation was previously stored in session, then we
        if self.session_key in self.session:
            # rebuild the cart object from that serialized representation.
            cart_representation = self.session[self.session_key]
            ids_in_cart = cart_representation.keys()
            equipments_queryset = self.get_queryset().filter(pk__in=ids_in_cart)
            for equipment in equipments_queryset:
                item = cart_representation[str(equipment.pk)]
                self._items_dict[equipment.pk] = CartItem(
                    equipment
                )

    def __contains__(self, equipment):
        """
        Checks if the given product is in the cart.
        """
        return equipment in self.equipment

    def get_equipment_model(self):
        return module_loading.get_equipment_model()

    def filter_equipments(self, queryset):
        """
        Applies lookup parameters defined in settings.
        """
        lookup_parameters = getattr(settings, 'CART_PRODUCT_LOOKUP', None)
        if lookup_parameters:
            queryset = queryset.filter(**lookup_parameters)
        return queryset

    def get_queryset(self):
        equipment_model = self.get_equipment_model()
        queryset = equipment_model._default_manager.all()
        queryset = self.filter_equipments(queryset)
        return queryset

    def update_session(self):
        """
        Serializes the cart data, saves it to session and marks session as modified.
        """
        self.session[self.session_key] = self.cart_serializable
        self.session.modified = True

    def add(self, equipment):
        """
        Adds or creates products in cart. For an existing product,
        the quantity is increased and the price is ignored.
        """
        if equipment in self.equipments:
            self.equipment = equipment
        else:
            self._items_dict[equipment.pk] = CartItem(equipment)
        self.update_session()

    def remove(self, equipment):
        """
        Removes the product.
        """
        if equipment in self.equipments:
            del self._items_dict[equipment.pk]
            self.update_session()

    def clear(self):
        """
        Removes all items.
        """
        self._items_dict = {}
        self.update_session()

    @property
    def items(self):
        """
        The list of cart items.
        """
        return self._items_dict.values()

    @property
    def cart_serializable(self):
        """
        The serializable representation of the cart.
        For instance:
        {
            '1': {'product_pk': 1, 'quantity': 2, price: '9.99'},
            '2': {'product_pk': 2, 'quantity': 3, price: '29.99'},
        }
        Note how the product pk servers as the dictionary key.
        """
        cart_representation = {}
        for item in self.items:
            # JSON serialization: object attribute should be a string
            equipment_id = str(item.equipment.pk)
            cart_representation[equipment_id] = item.to_dict()
        return cart_representation


    @property
    def items_serializable(self):
        """
        The list of items formatted for serialization.
        """
        return self.cart_serializable.items()

    @property
    def unique_count(self):
        """
        The number of unique items in cart, regardless of the quantity.
        """
        return len(self._items_dict)

    @property
    def is_empty(self):
        return self.unique_count == 0

    @property
    def equipments(self):
        """
        The list of associated products.
        """
        return [item.equipment for item in self.items]

