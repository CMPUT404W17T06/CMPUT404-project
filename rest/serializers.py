# Author: Braedy Kuzma

from django.core.paginator import Paginator
from rest_framework import serializers

from dash.models import Post, Author, Comment, Category

class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = ('id', 'host', 'url', 'github')

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

        # The source and the origin is the same as the id -- so says the Hindle
        rv['source'] = rv['id']
        rv['origin'] = rv['id']

        # Get comments and add count to rv
        comments = Comment.objects.filter(post=post)
        count = comments.count()
        rv['count'] = count

        # Get number of comments to attach and add to rv
        pageSize = self.context.get('commentPageSize', 50)
        rv['size'] = pageSize if count > pageSize else count

        # Serialize and attach the first page
        pager = Paginator(comments, pageSize)
        commSer = CommentSerializer(pager.page(1), many=True)
        rv['comments'] = commSer.data

        return rv

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('author', 'comment', 'contentType', 'published', 'id')
    author = AuthorSerializer()
