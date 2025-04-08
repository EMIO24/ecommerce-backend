from rest_framework import serializers
from .models import Product, Category, Order, OrderItem, Review


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model.
    """
    class Meta:
        model = Category
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    """
    Serializer for the Product model.
    Allows setting the category using its primary key.
    """
    category = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        required=False,
        allow_null=True
    )

    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('created_date',)


class OrderItemSerializer(serializers.ModelSerializer):
    """
    Serializer for the OrderItem model.
    Allows setting the item (product) using its primary key during write operations.
    Displays the item ID in the output.
    """
    item = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), write_only=True)
    item_output = serializers.SerializerMethodField(method_name='get_item', read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'item', 'quantity', 'item_output']
        read_only_fields = ['id', 'item_output']

    def get_item(self, obj):
        """
        Returns the ID of the associated product.
        """
        return obj.product.id

    def to_representation(self, instance):
        """
        Overrides the default representation to use 'item' instead of 'item_output' in the output.
        This is done to have a consistent 'item' field in both input and output (though input uses PK).
        """
        representation = super().to_representation(instance)
        representation['item'] = representation.pop('item_output')
        return representation


class OrderSerializer(serializers.ModelSerializer):
    """
    Serializer for the Order model.
    Allows creating orders with multiple order items.
    """
    items = OrderItemSerializer(many=True, write_only=True)  # Allow creating items during order creation

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'items']
        read_only_fields = ['id', 'order_date', 'user']

    def create(self, validated_data):
        """
        Creates a new Order instance and its associated OrderItems.
        Manages stock quantity and raises a validation error if insufficient stock.
        """
        items_data = validated_data.pop('items')
        order = Order.objects.create(**validated_data)

        for item_data in items_data:
            product = item_data['item']
            quantity = item_data['quantity']
            if product.stock_quantity >= quantity:
                OrderItem.objects.create(order=order, product=product, quantity=quantity)
                product.stock_quantity -= quantity
                product.save()
            else:
                raise serializers.ValidationError(f"Insufficient stock for {product.name}")

        return order

    def to_representation(self, instance):
        """
        Overrides the default representation to include serialized OrderItem data.
        """
        representation = super().to_representation(instance)
        order_items = instance.orderitem_set.all()  # Ensure we are using the related manager
        representation['items'] = [OrderItemSerializer(item).data for item in order_items]
        return representation


class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model.
    Displays the username of the reviewer and sets user as read-only on creation.
    """
    user = serializers.ReadOnlyField(source='user.username')  # Display username, not ID

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
        