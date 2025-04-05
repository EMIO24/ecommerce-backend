from rest_framework import serializers
from .models import Product, Category, Order, OrderItem, Review


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'
        
     
class ProductSerializer(serializers.ModelSerializer):
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
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')

    class Meta:
        model = OrderItem
        fields = ['product_id', 'quantity']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = ['id', 'user', 'order_date', 'items']
        read_only_fields = ['id', 'order_date', 'user']

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        user = self.context['request'].user
        order = Order.objects.create(user=user, **validated_data)
        for item_data in items_data:
            product = item_data['product']
            quantity = item_data['quantity']
            if product.stock_quantity >= quantity:
                OrderItem.objects.create(order=order, product=product, quantity=quantity)
                product.stock_quantity -= quantity
                product.save()
            else:
                raise serializers.ValidationError(f"Insufficient stock for {product.name}")
        return order

class ReviewSerializer(serializers.ModelSerializer):
    user = serializers.ReadOnlyField(source='user.username') # Display username, not ID

    class Meta:
        model = Review
        fields = ['id', 'product', 'user', 'rating', 'text', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
