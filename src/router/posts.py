from typing import Annotated, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, Form, UploadFile, File
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database import get_db
from src.models.user import User
from src.models.post import Post
from src.models.comment import Comment
from src.models.like import Like
from src.schemas import PostResponse, CommentCreate, CommentResponse
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
    
    setattr(new_post, "likes_count", 0)
    setattr(new_post, "comments_count", 0)
    setattr(new_post, "is_liked", False)
    setattr(new_post, "user", format_author(new_post.user))
    
    return new_post

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

    for post in posts:
        likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        is_liked = (
            db.query(Like)
            .filter(Like.post_id == post.id, Like.user_id == current_user.User_ID)
            .first() is not None
        )
        setattr(post, "likes_count", likes_count)
        setattr(post, "comments_count", comments_count)
        setattr(post, "is_liked", is_liked)
        setattr(post, "user", format_author(post.user))

    return posts

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
    
    for post in posts:
        likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        comments_count = db.query(Comment).filter(Comment.post_id == post.id).count()
        is_liked = db.query(Like).filter(Like.post_id == post.id, Like.user_id == current_user.User_ID).first() is not None
        
        setattr(post, "likes_count", likes_count)
        setattr(post, "comments_count", comments_count)
        setattr(post, "is_liked", is_liked)
        setattr(post, "user", format_author(post.user))
        
    return posts

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
    
    setattr(new_comment, "user", format_author(new_comment.user))
    comments_count = db.query(Comment).filter(Comment.post_id == post_id).count()
    comment_dict = CommentResponse.model_validate(new_comment).model_dump(by_alias=True)
    comment_dict["commentsCount"] = comments_count
    return comment_dict

@router.get("/{post_id}/comments", response_model=list[CommentResponse])
def get_comments(
    post_id: int,
    db: DB,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: User = Depends(get_current_user),
):
    """Get comments of a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    comments = db.query(Comment).filter(Comment.post_id == post_id).order_by(desc(Comment.created_at)).offset(skip).limit(limit).all()
    for comment in comments:
        setattr(comment, "user", format_author(comment.user))
        
    return comments
