"""Base channel revision

Revision ID: ce0afa34bb39
Revises:
Create Date: 2022-11-14 11:32:08.227267

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "ce0afa34bb39"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "channel",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_channel")),
        schema="plugin_channels",
    )
    op.create_table(
        "channel_character",
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["plugin_channels.channel.id"],
            name=op.f("fk_channel_character_channel_id_channel"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["core.character.id"],
            name=op.f("fk_channel_character_character_id_character"),
        ),
        sa.PrimaryKeyConstraint(
            "channel_id", "character_id", name=op.f("pk_channel_character")
        ),
        schema="plugin_channels",
    )
    op.create_table(
        "channel_message",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("message", sa.String(), nullable=False),
        sa.Column("character_id", sa.UUID(), nullable=False),
        sa.Column("channel_id", sa.UUID(), nullable=False),
        sa.Column("timestamp", sa.TIMESTAMP(timezone=True), nullable=False),
        sa.Column("system", sa.Boolean(), nullable=False),
        sa.ForeignKeyConstraint(
            ["channel_id"],
            ["plugin_channels.channel.id"],
            name=op.f("fk_channel_message_channel_id_channel"),
        ),
        sa.ForeignKeyConstraint(
            ["character_id"],
            ["core.character.id"],
            name=op.f("fk_channel_message_character_id_character"),
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_channel_message")),
        schema="plugin_channels",
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("channel_message", schema="plugin_channels")
    op.drop_table("channel_character", schema="plugin_channels")
    op.drop_table("channel", schema="plugin_channels")
    # ### end Alembic commands ###