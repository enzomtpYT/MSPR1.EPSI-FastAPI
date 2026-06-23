from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database import get_db
from src.models.user import User
from src.models.post import Post
from src.models.comment import Comment
from src.models.like import Like
from src.schemas import PostResponse, CommentCreate, CommentResponse, UserBasicInfo
from src.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])
DB = Annotated[Session, Depends(get_db)]

def format_author(user: User | None) -> dict | None:
    if not user:
        return None
    return {
        "User_ID": user.User_ID,
        "displayName": user.User_DisplayName,
        "email": user.User_mail,
        "avatar": user.profile_picture_url
    }

@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    db: DB,
    content: str = Form(""),
    mediaType: str = Form("none"),
    media: list[UploadFile] = File(None),
    current_user: User = Depends(get_current_user),
):
    """Create a new post."""
    media_urls = []
    if media:
        media_urls = [file.filename for file in media if file and file.filename]

    new_post = Post(
        user_id=current_user.User_ID,
        content=content,
        media_type=mediaType,
        media_urls=media_urls if media_urls else None,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    return {
        "id": new_post.id,
        "user_id": new_post.user_id,
        "content": new_post.content,
        "media_type": new_post.media_type,
        "media_urls": new_post.media_urls,
        "created_at": new_post.created_at,
        "updated_at": getattr(new_post, "updated_at", None),
        "likes_count": 0,
        "comments_count": 0,
        "is_liked": False,
        "user": format_author(new_post.user)
    }

@router.get("/me", response_model=list[PostResponse])
def get_my_posts(
    db: DB,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get the current user's own posts."""
    posts = (
        db.query(Post)
        .filter(Post.user_id == current_user.User_ID)
        .order_by(desc(Post.created_at))
        .offset(skip)
        .limit(limit)
        .all()
    )

    result = []
    for post in posts:
        likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        is_liked = (
            db.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == current_user.User_ID)
            .first() is not None
        )
        result.append({
            "id": post.id,
            "user_id": post.user_id,
            "content": post.content,
            "media_type": post.media_type,
            "media_urls": post.media_urls,
            "created_at": post.created_at,
            "updated_at": getattr(post, "updated_at", None),
            "likes_count": likes_count,
            "comments_count": comments_count,
            "is_liked": is_liked,
            "user": format_author(post.user)
        })

    return result

@router.delete("/{post_id}", status_code=204)
def delete_post(
    post_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Delete a post (author or admin only)."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.user_id != current_user.User_ID and not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this post")
    db.delete(post)
    db.commit()

@router.get("/", response_model=list[PostResponse])
def get_posts(
    db: DB,
    search: str = Query(None),
    sort: str = Query("date", pattern="^(date|hot|likes)$"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get posts with search and sort."""
    query = db.query(Post)
    
    if search:
        query = query.filter(Post.content.ilike(f"%{search}%"))
        
    if sort == "likes" or sort == "hot":
        query = query.outerjoin(Like).group_by(Post.id).order_by(desc(func.count(Like.user_id)))
    else:
        # default to date
        query = query.order_by(desc(Post.created_at))
        
    posts = query.offset(skip).limit(limit).all()
    
    result = []
    for post in posts:
        likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.User_ID).first() is not None
        
        result.append({
            "id": post.id,
            "user_id": post.user_id,
            "content": post.content,
            "media_type": post.media_type,
            "media_urls": post.media_urls,
            "created_at": post.created_at,
            "updated_at": getattr(post, "updated_at", None),
            "likes_count": likes_count,
            "comments_count": comments_count,
            "is_liked": is_liked,
            "user": format_author(post.user)
        })
        
    return result

@router.post("/{post_id}/like", status_code=200)
def toggle_like_post(
    post_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Toggle like on a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    existing_like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.User_ID).first()
    
    is_liked = False
    if existing_like:
        db.delete(existing_like)
    else:
        new_like = Like(post_id=post_id, user_id=current_user.User_ID)
        db.add(new_like)
        is_liked = True
        
    db.commit()
    
    likes_count = db.query(Like).filter(Like.post_id == post_id).count()
    return {"isLiked": is_liked, "likesCount": likes_count}

@router.post("/{post_id}/comments", status_code=201)
def add_comment(
    post_id: int,
    payload: CommentCreate,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a post. Returns the comment plus updated commentsCount."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    new_comment = Comment(
        user_id=current_user.User_ID,
        post_id=post_id,
        content=payload.text
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    
    comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    return {
        "id": new_comment.id,
        "user_id": new_comment.user_id,
        "post_id": new_comment.post_id,
        "content": new_comment.content,
        "created_at": new_comment.created_at,
        "updated_at": getattr(new_comment, "updated_at", None),
        "user": format_author(new_comment.user),
        "commentsCount": comments_count
    }

@router.get("/{post_id}/comments", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    db: DB,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("desc", pattern="^(asc|desc)$"),
    current_user: User = Depends(get_current_user),
):
    """Get comments of a post, ordered by created_at asc or desc."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    order = Comment.created_at.asc() if sort == "asc" else Comment.created_at.desc()
    comments = (
        db.query(Comment)
        .filter(Comment.post_id == post_id)
        .order_by(order)
        .offset(skip)
        .limit(limit)
        .all()
    )
    result = []
    for comment in comments:
        result.append({
            "id": comment.id,
            "user_id": comment.user_id,
            "post_id": comment.post_id,
            "content": comment.content,
            "created_at": comment.created_at,
            "updated_at": getattr(comment, "updated_at", None),
            "user": format_author(comment.user)
        })

    return result


@router.delete("/{post_id}/comments/{comment_id}", status_code=204)
def delete_comment(
    post_id: int,
    comment_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Delete a comment (author or admin only)."""
    comment = (
        db.query(Comment)
        .filter(Comment.id == comment_id, Comment.post_id == post_id)
        .first()
    )
    if not comment:
        raise HTTPException(status_code=404, detail="Comment not found")
    if comment.user_id != current_user.User_ID and not current_user.isAdmin:
        raise HTTPException(status_code=403, detail="Not authorized to delete this comment")
    db.delete(comment)
    db.commit()


@router.get("/{post_id}/likes", response_model=list[UserBasicInfo])
def get_post_likes(
    post_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Return the list of users who liked a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    likes = db.query(Like).filter(Like.post_id == post_id).all()
    users = []
    for like in likes:
        user = like.user
        if user:
            # Build a dict that satisfies UserBasicInfo's validation_alias fields
            users.append({
                "User_ID": user.User_ID,
                "User_DisplayName": user.User_DisplayName,
                "User_mail": user.User_mail,
                "profile_picture_url": user.profile_picture_url,
            })
    return [UserBasicInfo.model_validate(u) for u in users]
