from rest_framework import serializers



class ListTransactionOutputNestedSerializer(serializers.Serializer):
    date = serializers.DateField()
    amount = serializers.DecimalField(max_digits=12, decimal_places=2)
    transactions = serializers.ListField(child=serializers.DictField())