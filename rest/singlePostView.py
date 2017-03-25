# Author: Braedy Kuzma

from rest_framework.views import APIView

from dash.models import Post, Author, Category, CanSee
from .serializers import PostSerializer
from .verifyUtils import postValidators, NotFound, ResourceConflict
from .dataUtils import validateData, pidToUrl, getPostData, getPost
from .httpUtils import JSONResponse

class PostView(APIView):
    """
    REST view of an individual Post.
    """
    def delete(self, request, pid=None):
        """
        Deletes a post.
        """
        # Get the post
        post = getPost(request, pid)

        # Save the id for the return
        postId = post.id

        # Delete the post
        post.delete()

        # Return
        data = {'deleted': postId}
        return JSONResponse(data)

    def get(self, request, pid=None):
        """
        Gets a post.
        """
        # Get post
        post = getPost(request, pid)

        # Serialize post
        postSer = PostSerializer(post)
        postData = postSer.data

        # TODO: Add query?
        # postData['query'] = 'post'

        return JSONResponse(postData)

    def post(self, request, pid=None):
        """
        Creates a post.
        """
        try:
            # This has the potential to raise NotFound AND MalformedId
            # If it's MalformedId we want it to fail
            post = getPost(request, pid)
        # We WANT it to be not found
        except NotFound:
            pass
        # No error was raised which means it already exists
        else:
            raise ResourceConflict('post',
                                   request.build_absolute_uri(request.path))

        # Get and validate data
        data = getPostData(request)
        validateData(data, postValidators)

        # Get id url
        url = pidToUrl(request, pid)

        # Fill in required fields
        post = Post()
        post.id = url
        post.title = data['title']
        post.contentType = data['contentType']
        post.content = data['content']
        post.author = Author.objects.get(id=data['author'])
        post.visibility = data['visibility']

        # Fill in unrequired fields
        post.unlisted = data.get('unlisted', False)
        post.description = data.get('description', '')
        post.published = data.get('published', timezone.now())

        # Save
        post.save()

        # Were there any categories?
        if 'categories' in data and data['categories']:
            categoryList = data['categories']

            # Build Category objects
            for categoryStr in categoryList:
                category = Category()
                category.category = categoryStr
                category.post = post
                category.save()

        # Were there any users this should be particularly visibleTo
        if 'visibleTo' in data and data['visibleTo']:
            visibleToList = data['visibleTo']

            # Build can see list
            for authorId in visibleToList:
                canSee = CanSee()
                canSee.post = post
                canSee.visibleTo = authorId
                canSee.save()

        # Return
        data = {'created': post.id}
        return JSONResponse(data)

    def put(self, request, pid=None):
        """
        Updates a post.
        """
        # Get post
        post = getPost(request, pid)

        # Get data from PUT, don't require any fields
        data = getPostData(request, require=False)
        validateData(data, postValidators)

        # Update fields as appropriate
        post.title = data.get('title', post.title)
        post.description = data.get('description', post.description)
        post.published = data.get('published', post.published)
        post.contentType = data.get('contentType', post.contentType)
        post.content = data.get('content', post.content)
        post.author = Author.objects.get(id=data['author']) \
                      if 'author' in data else \
                      post.author
        post.visibility = data.get('visibility', post.visibility)
        post.unlisted = data.get('unlisted', post.unlisted)

        post.save()

        # Should we update categories?
        if 'categories' in data:
            # Destroy the old categories
            oldCategories = Category.objects.filter(post=post)
            for category in oldCategories:
                category.delete()

            # Build new categories
            categoryList = data['categories']

            # Build Category objects
            for categoryStr in categoryList:
                category = Category()
                category.category = categoryStr
                category.post = post
                category.save()

        # Should we update the visibleTos?
        if 'visibleTo' in data:
            # Destroy old can sees
            oldCanSees = CanSee.objects.filter(post=post)
            for canSee in oldCanSees:
                canSee.delete()

            # Build new can sees
            visibleToList = data['visibleTo']

            # Build can see list
            for authorId in visibleToList:
                canSee = CanSee()
                canSee.post = post
                canSee.visibleTo = authorId
                canSee.save()

        # Return
        data = {'updated': post.id}
        return JSONResponse(data)
