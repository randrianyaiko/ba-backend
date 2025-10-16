def reorder_products(products, recommended_ids):
    """
    Reorder products so recommended_ids appear first (in given order),
    then all other products follow.
    """
    if not recommended_ids:
        return products

    recommended_ids = [str(rid) for rid in recommended_ids if rid]
    rec_set = set(recommended_ids)

    rec_part = [p for pid in recommended_ids for p in products if p['product_id'] == pid]
    non_rec_part = [p for p in products if p['product_id'] not in rec_set]

    return rec_part + non_rec_part
