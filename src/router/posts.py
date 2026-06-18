from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc

from src.database import get_db
from src.models.user import User
from src.models.post import Post
from src.models.comment import Comment
from src.models.like import Like
from src.schemas import PostCreate, PostResponse, CommentCreate, CommentResponse
from src.auth import get_current_user

router = APIRouter(prefix="/posts", tags=["posts"])
DB = Annotated[Session, Depends(get_db)]

@router.post("/", response_model=PostResponse, status_code=201)
def create_post(
    payload: PostCreate,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Create a new post."""
    new_post = Post(
        user_id=current_user.User_ID,
        content=payload.content,
        media_type=payload.media_type,
        media_urls=payload.media_urls,
    )
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    
    setattr(new_post, "likes_count", 0)
    return new_post

@router.get("/feed", response_model=list[PostResponse])
def get_feed(
    db: DB,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    sort: str = Query("new", pattern="^(new|popular)$"),
    current_user: User = Depends(get_current_user),
):
    """Get the news feed."""
    query = db.query(Post)
    
    if sort == "popular":
        query = query.outerjoin(Like).group_by(Post.id).order_by(desc(func.count(Like.user_id)))
    else:
        query = query.order_by(desc(Post.created_at))
        
    posts = query.offset(skip).limit(limit).all()
    
    for post in posts:
        likes_count = db.query(Like).filter(Like.post_id == post.id).count()
        setattr(post, "likes_count", likes_count)
        
    return posts

@router.post("/{post_id}/like", status_code=201)
def like_post(
    post_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Like a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    existing_like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.User_ID).first()
    if existing_like:
        raise HTTPException(status_code=400, detail="Post already liked")
        
    new_like = Like(post_id=post_id, user_id=current_user.User_ID)
    db.add(new_like)
    db.commit()
    return {"message": "Post liked"}

@router.delete("/{post_id}/like", status_code=204)
def unlike_post(
    post_id: int,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Unlike a post."""
    like = db.query(Like).filter(Like.post_id == post_id, Like.user_id == current_user.User_ID).first()
    if not like:
        raise HTTPException(status_code=404, detail="Like not found")
        
    db.delete(like)
    db.commit()

@router.post("/{post_id}/comments", response_model=CommentResponse, status_code=201)
def add_comment(
    post_id: int,
    payload: CommentCreate,
    db: DB,
    current_user: User = Depends(get_current_user),
):
    """Add a comment to a post."""
    post = db.query(Post).filter(Post.id == post_id).first()
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
        
    new_comment = Comment(
        user_id=current_user.User_ID,
        post_id=post_id,
        content=payload.content
    )
    db.add(new_comment)
    db.commit()
    db.refresh(new_comment)
    return new_comment

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
    return comments
