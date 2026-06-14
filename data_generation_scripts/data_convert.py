import json
import csv
import os


def convert_json_to_rag_formats():
    print("Starting conversion of JSON files...")

    # 1. Load Inventory to build a SKU -> Name lookup dictionary
    # This is crucial so we can replace raw SKUs with actual product names in the text files.
    sku_to_name = {}
    try:
        with open('inventory.json', 'r', encoding='utf-8') as f:
            inv_data = json.load(f)
            for item in inv_data:
                sku_to_name[item['sku']] = item['product_name']
    except FileNotFoundError:
        print("Error: inventory.json not found. Make sure the JSON files are in the directory.")
        return

    # 2. Convert Inventory to CSV
    print("Converting inventory.json -> inventory.csv")
    with open('../data/inventory.csv', 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(
            ["SKU", "Product_Name", "Brand", "Category", "Stock_Count", "Price", "Aisle", "Section", "Shelf"])
        for item in inv_data:
            writer.writerow([
                item.get('sku', ''),
                item.get('product_name', ''),
                item.get('brand', ''),
                item.get('category', ''),
                item.get('qty_on_hand', 0),
                item.get('selling_price', 0.0),
                f"{item.get('aisle_code', '')} - {item.get('aisle_name', '')}",
                item.get('section', ''),
                item.get('shelf', '')
            ])

    # 3. Convert Offers to CSV
    print("Converting offers.json -> offers.csv")
    try:
        with open('../raw_data/offers.json', 'r', encoding='utf-8') as f:
            offers_data = json.load(f)

        with open('../data/offers.csv', 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(
                ["Offer_ID", "SKU", "Product_Name", "Offer_Type", "Description", "Offer_Price", "Promo_Tag"])
            for offer in offers_data:
                writer.writerow([
                    offer.get('offer_id', ''),
                    offer.get('sku', ''),
                    offer.get('product_name', ''),
                    offer.get('offer_type', ''),
                    offer.get('description', ''),
                    offer.get('offer_price', ''),
                    offer.get('promo_tag', '')
                ])
    except FileNotFoundError:
        print("Warning: offers.json not found.")

    # 4. Convert Substitutions to TXT (Replacing SKUs with Names)
    print("Converting substitutions.json -> substitutes.txt")
    try:
        with open('../raw_data/substitutions.json', 'r', encoding='utf-8') as f:
            subs_data = json.load(f)

        with open('../data/substitutes.txt', 'w', encoding='utf-8') as f:
            f.write("=== PRODUCT SUBSTITUTION MAPPINGS ===\n\n")
            for sub in subs_data:
                product = sub.get('product_name', 'Unknown Product')
                reason = sub.get('reason', 'Alternative option')

                # Resolve substitute SKUs to human-readable names
                sub_names = []
                for s_sku in sub.get('substitutes', []):
                    sub_names.append(sku_to_name.get(s_sku, s_sku))

                f.write(f"Target Product: {product} ({sub.get('sku', '')})\n")
                f.write(f"Reason for Substitution: {reason}\n")
                f.write(f"Approved Substitutes: {', '.join(sub_names)}\n\n")
    except FileNotFoundError:
        print("Warning: substitutions.json not found.")

    # 5. Convert SOPs to TXT
    print("Converting sops.json -> SOP.txt")
    try:
        with open('../raw_data/sops.json', 'r', encoding='utf-8') as f:
            sops_data = json.load(f)

        with open('../data/SOP.txt', 'w', encoding='utf-8') as f:
            f.write("=== GENERAL STORE STANDARD OPERATING PROCEDURES (SOP) ===\n\n")
            for sop in sops_data:
                f.write(
                    f"[{sop.get('sop_id', '')}] TITLE: {sop.get('title', '')} (Dept: {sop.get('department', '')})\n")
                steps = sop.get('steps', [])
                for i, step in enumerate(steps, 1):
                    f.write(f"  Step {i}: {step}\n")
                f.write("\n")
    except FileNotFoundError:
        print("Warning: sops.json not found.")

    # 6. Convert Planogram to TXT (Replacing Adjacency SKUs with Names)
    print("Converting planogram.json -> planogram.txt")
    try:
        with open('../raw_data/planogram.json', 'r', encoding='utf-8') as f:
            plano_data = json.load(f)

        with open('../data/planogram.txt', 'w', encoding='utf-8') as f:
            f.write("=== STORE PLANOGRAM & PRODUCT PLACEMENT LAYOUT ===\n\n")
            for item in plano_data:
                product = item.get('product_name', '')
                location = f"Aisle {item.get('aisle_code', '')} ({item.get('aisle_name', '')}), Section {item.get('section', '')}, {item.get('shelf', '')}"

                # Resolve adjacent SKUs to human-readable names
                adj_names = []
                for a_sku in item.get('adjacents', []):
                    adj_names.append(sku_to_name.get(a_sku, a_sku))

                f.write(f"Product: {product} (SKU: {item.get('sku', '')})\n")
                f.write(f"Exact Location: {location}\n")
                f.write(f"Facing Count: {item.get('facing_count', 1)}\n")
                f.write(f"Placed Adjacent To: {', '.join(adj_names) if adj_names else 'None'}\n")
                f.write(f"Merchandising Notes: {item.get('notes', 'None')}\n\n")
    except FileNotFoundError:
        print("Warning: planogram.json not found.")

    print(
        "Data conversion complete! Output files generated: inventory.csv, offers.csv, substitutes.txt, SOP.txt, planogram.txt")


if __name__ == "__main__":
    convert_json_to_rag_formats()