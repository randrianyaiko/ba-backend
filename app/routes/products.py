# app/routes/products.py
import requests
from sqlalchemy import or_
from flask import Blueprint, request, jsonify
from app.config import Config
from app.database import get_session
from app.models import Product
from app.services.activity import track_activity
from app.services.product import (
    create_product,
    get_product,
    get_products,
    get_products_by_ids,
)
from app.utils.decorators import verify_token as decode_token  # helper to decode token if present

# Import the recommender system
from src.recommender.recommender import SparseRecommender

products_bp = Blueprint("products", __name__)

# ------------------------
# Routes
# ------------------------

@products_bp.route("/products", methods=["GET"])
def get_products_route():
    try:
        page = int(request.args.get("page", 1))
        per_page = int(request.args.get("per_page", 6))
        search_query = request.args.get("q")
        category = request.args.get("category")

        recommended_products = []
        recommended_ids = []

        # Optional Authorization header
        auth_header = request.headers.get("Authorization")

        # --------------------------------
        # STEP 1: Get recommended products
        # --------------------------------
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            current_user = decode_token(token)

            try:
                if current_user:
                    user_id = current_user.get("user_id")

                    # Initialize recommender system
                    recommender = SparseRecommender(top_k_similar_users=5, top_k_items=10)

                    # Get recommended item indices (product IDs)
                    recommendations = recommender.recommend(user_id)

                    # recommendations is a list of tuples: [(index, score), ...]
                    recommended_ids = [idx for idx, _ in recommendations]

                    if recommended_ids:
                        # Fetch full product objects by their IDs
                        recommended_result = get_products_by_ids(recommended_ids)

                        # Handle both dicts and model instances
                        recommended_products = [
                            p.to_dict() if hasattr(p, "to_dict") else p
                            for p in recommended_result
                        ]

            except Exception as e:
                print(f"Error occurred during recommendation: {e}")
                # Don't stop the endpoint if recommendations fail — fallback to normal products
                recommended_products = []
                recommended_ids = []

        # --------------------------------
        # STEP 2: Fill remaining slots with regular products
        # --------------------------------
        remaining_slots = per_page - len(recommended_products)
        regular_products = []
        if remaining_slots > 0:
            regular_result = get_products(
                page=page,
                per_page=remaining_slots,
                search_query=search_query,
                category=category,
                exclude_ids=recommended_ids,
            )
            regular_products = regular_result["products"]

        # --------------------------------
        # STEP 3: Merge and paginate
        # --------------------------------
        paginated_products = recommended_products[:per_page] + regular_products

        # Compute total items and pages
        total_items_result = get_products(
            page=1, per_page=1, search_query=search_query, category=category
        )
        total_items = total_items_result["total_items"]
        total_pages = (total_items + per_page - 1) // per_page

        return (
            jsonify(
                {
                    "products": paginated_products,
                    "total_pages": total_pages,
                    "current_page": page,
                    "total_items": total_items,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in get_products_route: {e}")
        return jsonify({"message": str(e)}), 500


@products_bp.route("/products/<product_id>", methods=["GET"])
def get_product_route(product_id):
    try:
        product = get_product(product_id)
        if not product:
            return jsonify({"message": "Product not found"}), 404

        # Optional activity tracking if token is present
        auth_header = request.headers.get("Authorization")
        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            current_user = decode_token(token)
            if current_user:
                track_activity(current_user["user_id"], "VIEW", product_id)

        return (
            jsonify(product.to_dict() if hasattr(product, "to_dict") else product),
            200,
        )

    except Exception as e:
        print(f"Error in get_product_route: {e}")
        return jsonify({"message": str(e)}), 500


@products_bp.route("/products/create", methods=["POST"])
def create_product_route():
    try:
        data = request.get_json()
        product = create_product(data)
        return jsonify(product.to_dict() if hasattr(product, "to_dict") else product), 201
    except Exception as e:
        return jsonify({"message": str(e)}), 500

@products_bp.route("/products/recommend", methods=["GET"])
def recommend():
    """
    Get personalized product recommendations for the authenticated user.
    Requires Authorization header: Bearer <token>
    """
    try:
        # -------------------------------
        # STEP 1: Validate token & extract user
        # -------------------------------
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"message": "Authorization token is missing"}), 401

        token = auth_header.split(" ")[1]
        current_user = decode_token(token)

        if not current_user or "user_id" not in current_user:
            return jsonify({"message": "Invalid or expired token"}), 401

        user_id = current_user["user_id"]

        # -------------------------------
        # STEP 2: Get recommendations
        # -------------------------------
        recommender = SparseRecommender(top_k_similar_users=10, top_k_items=10)
        recommendations = recommender.recommend(user_id)

        if not recommendations:
            return jsonify({"message": "No recommendations found"}), 200

        # recommendations = [(product_id, score), ...]
        recommended_ids = [idx for idx, _ in recommendations]

        # -------------------------------
        # STEP 3: Fetch product details
        # -------------------------------
        recommended_result = get_products_by_ids(recommended_ids)
        recommended_products = [
            p.to_dict() if hasattr(p, "to_dict") else p for p in recommended_result
        ]

        # Optionally attach scores to each product
        score_map = dict(recommendations)
        for product in recommended_products:
            pid = product.get("id") if isinstance(product, dict) else getattr(product, "id", None)
            if pid in score_map:
                product["score"] = score_map[pid]

        # -------------------------------
        # STEP 4: Return JSON response
        # -------------------------------
        return (
            jsonify(
                {
                    "user_id": user_id,
                    "total_recommended": len(recommended_products),
                    "recommended_products": recommended_products,
                }
            ),
            200,
        )

    except Exception as e:
        print(f"Error in /products/recommend: {e}")
        return jsonify({"message": str(e)}), 500
