import uuid
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.models.family import Family, FamilyMember, FamilyMemberRole
from app.schemas.family import (
    FamilyCreate, FamilyResponse, InviteMemberRequest,
    UpdatePrivacyRequest, FamilyMemberResponse
)

router = APIRouter(prefix="/families", tags=["families"])


@router.post("/", response_model=FamilyResponse, status_code=201)
async def create_family(
    body: FamilyCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    family = Family(owner_id=current_user.id, name=body.name)
    db.add(family)
    await db.flush()

    # Owner is automatically a member
    db.add(FamilyMember(
        family_id=family.id,
        user_id=current_user.id,
        role=FamilyMemberRole.owner,
    ))
    await db.commit()
    await db.refresh(family)
    return family


@router.get("/{family_id}", response_model=FamilyResponse)
async def get_family(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_member(db, family_id, current_user.id)
    result = await db.execute(select(Family).where(Family.id == family_id))
    return result.scalar_one_or_none() or _not_found()


@router.get("/{family_id}/members", response_model=list[FamilyMemberResponse])
async def list_members(
    family_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_member(db, family_id, current_user.id)
    result = await db.execute(
        select(FamilyMember).where(FamilyMember.family_id == family_id)
    )
    return result.scalars().all()


@router.post("/{family_id}/invite", status_code=200)
async def invite_member(
    family_id: uuid.UUID,
    body: InviteMemberRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_admin(db, family_id, current_user.id)

    user_result = await db.execute(
        select(User).where(User.phone == body.phone, User.deleted_at.is_(None))
    )
    invitee = user_result.scalar_one_or_none()
    if not invitee:
        raise HTTPException(status_code=404, detail="User with this phone not found. They must register first.")

    existing = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == invitee.id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=409, detail="User already in family")

    db.add(FamilyMember(family_id=family_id, user_id=invitee.id, role=body.role))
    await db.commit()
    return {"message": f"User {body.phone} added to family"}


@router.put("/{family_id}/members/{member_id}/privacy", status_code=200)
async def update_member_privacy(
    family_id: uuid.UUID,
    member_id: uuid.UUID,
    body: UpdatePrivacyRequest,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    # Only owner/admin OR the member themselves can update privacy
    await _assert_member(db, family_id, current_user.id)

    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == member_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")

    member.privacy = {"hide_from": body.hide_from}
    await db.commit()
    return {"message": "Privacy settings updated"}


@router.delete("/{family_id}/members/{member_id}", status_code=204)
async def remove_member(
    family_id: uuid.UUID,
    member_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    await _assert_admin(db, family_id, current_user.id)
    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == member_id,
        )
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Member not found")
    if member.role == FamilyMemberRole.owner:
        raise HTTPException(status_code=400, detail="Cannot remove family owner")
    await db.delete(member)
    await db.commit()


async def _assert_member(db: AsyncSession, family_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == user_id,
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Not a member of this family")


async def _assert_admin(db: AsyncSession, family_id: uuid.UUID, user_id: uuid.UUID):
    result = await db.execute(
        select(FamilyMember).where(
            FamilyMember.family_id == family_id,
            FamilyMember.user_id == user_id,
            FamilyMember.role.in_([FamilyMemberRole.owner, FamilyMemberRole.admin]),
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=403, detail="Admin access required")


def _not_found():
    raise HTTPException(status_code=404, detail="Not found")
