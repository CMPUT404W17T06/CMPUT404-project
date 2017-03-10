# Author: Braedy Kuzma

from rest_framework import serializers
from dash.models import Post, Author, Comment, Category

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'host', 'url')

    def to_representation(self, author):
        rv = serializers.ModelSerializer.to_representation(self, author)
        rv['displayName'] = author.user.get_username()
        return rv

class CategorySerializer(serializers.BaseSerializer):
    def to_representation(self, category):
        return category.category

class PostSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = '__all__'
    author = AuthorSerializer()

    def to_representation(self, post):
        rv = serializers.ModelSerializer.to_representation(self, post)
        categories = Category.objects.filter(post=post)
        catSer = CategorySerializer(categories, many=True)
        rv['categories'] = catSer.data
        return rv

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id')
    author = AuthorSerializer()
