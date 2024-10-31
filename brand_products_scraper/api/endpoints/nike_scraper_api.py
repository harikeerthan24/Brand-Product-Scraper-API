import requests
from bs4 import BeautifulSoup
import json

# Function to fetch and parse the product page
def fetch_product_data(url):
    response = requests.get(url)
    response.raise_for_status()  # Raise an error for bad responses

    # Use BeautifulSoup to parse the HTML
    soup = BeautifulSoup(response.text, 'lxml')

    # Extract the JSON data from the <script> tag
    script = soup.find('script', id='__NEXT_DATA__')
    data = json.loads(script.string)

    page_props = data.get('props', {}).get('pageProps', {})
    products = page_props.get('selectedProduct', {})

    id = products.get('id', '')

    # Lists to hold active and inactive sizes
    active_sizes = []
    inactive_sizes = []

    # Extract sizes
    sizes = products.get('sizes', [])
    for size in sizes:
        status = size.get('status', '')
        label = size.get('localizedLabel', '')
        if status == 'ACTIVE':
            active_sizes.append(label)
        else:
            inactive_sizes.append(label)

    # Extract other product details
    color = products.get('colorDescription', '')
    price = products.get('prices', {}).get('currentPrice', 0)
    price = f"${price:.2f}"

    product_info = products.get('productInfo', {})
    title = product_info.get('title', '')
    subtitle = product_info.get('subtitle', '')
    product_description = product_info.get('productDescription', '')
    benefits = product_info.get('enhancedBenefits', [])
    product_url = product_info.get('url', '')

    # Extract media (images and videos)
    media = products.get('contentImages', [])
    images = []
    videos = []

    for item in media:
        if item["cardType"] == "image":
            images.append(item["properties"]["squarish"]["url"])
        elif item["cardType"] == "video":
            videos.append(item["properties"]["videoURL"])

    # Prepare the final output structure
    output_data = {
        "id": id,
        "product_name": title,
        "subtitle": subtitle,
        "product_description": product_description,
        "price": price,
        "product_url": product_url,
        "color": color,
        "active_sizes": active_sizes,
        "inactive_sizes": inactive_sizes,
        "benefits": benefits,
        "images": images,
        "videos": videos,
    }

    return output_data

# Example usage with multiple URLs
urls = [
    'https://www.nike.com/t/tatum-3-zero-days-off-basketball-shoes-vn4gkx/FZ6598-002',
    'https://www.nike.com/t/kd17-basketball-shoes-t6HTr6/FJ9487-002',
    'https://www.nike.com/t/air-jordan-xxxix-university-basketball-shoes-lCjzsl/FQ0213-400',
    'https://www.nike.com/t/kobe-8-big-kids-basketball-shoes-nT1p47/FN0266-400',
    'https://www.nike.com/t/lebron-witness-8-basketball-shoes-fSSfm4/FB2239-002',
    'https://www.nike.com/t/acg-therma-fit-fleece-pullover-hoodie-xblNtM/DH3087-104',
    'https://www.nike.com/t/jordan-brooklyn-fleece-mens-full-zip-hoodie-RM0JG1/FV7289-010',
    'https://www.nike.com/t/jordan-sport-hoop-fleece-mens-dri-fit-full-zip-hoodie-1wSKMN/FV8602-010',
    'https://www.nike.com/t/jordan-flight-fleece-mens-pullover-hoodie-47czXz/FV7249-368',
    'https://www.nike.com/t/jordan-flight-fleece-mens-pullover-hoodie-Rw6rPZ/FV7247-091',
    'https://www.nike.com/t/sportswear-club-fleece-pullover-hoodie-Bmrxdn/BV2654-718',
    'https://www.nike.com/t/sportswear-tech-fleece-mens-bomber-jacket-rXx6mF/FB8008-276',
    'https://www.nike.com/t/sabrina-fleece-basketball-hoodie-DwmbsT/FJ4449-019',
    'https://www.nike.com/t/jordan-dri-fit-sport-mens-full-zip-hoodie-1zhTd1/FD8119-010',
    'https://www.nike.com/t/jordan-brooklyn-fleece-mens-crew-neck-sweatshirt-X93KLz/FV7293-091',
    'https://www.nike.com/t/pro-womens-dri-fit-cropped-tank-top-Lmsp7K/FZ3615-338',
    'https://www.nike.com/t/one-fitted-womens-dri-fit-cropped-tank-top-C5z8Kc/FN2806-33',
    'https://www.nike.com/t/dri-fit-womens-t-shirt-plus-size-0hrrGj/FD0744-629',
    'https://www.nike.com/t/sportswear-womens-crew-neck-t-shirt-S47mjD/HQ2977-237',
    'https://www.nike.com/t/sportswear-chill-knit-womens-slim-long-sleeve-cropped-top-XXwQG7/HF5322-023',
    'https://www.nike.com/t/sportswear-womens-crew-neck-t-shirt-ddQhKB/HQ2976-341',
    'https://www.nike.com/t/womens-long-sleeve-graphic-basketball-t-shirt-5x5L9X/HF3259-100',
    'https://www.nike.com/t/tour-womens-golf-sweater-FPJFMF/DR5338-010',
    'https://www.nike.com/t/jordan-womens-tank-JnC4tt/DX4700-203',
    'https://www.nike.com/t/sportswear-essential-womens-oversized-long-sleeve-polo-21sJcf/FZ5813-051',
    'https://www.nike.com/t/v2k-run-mens-shoes-DDV2HS/HJ4497-200',
    'https://www.nike.com/t/tatum-3-zero-days-off-basketball-shoes-vn4gkx/FZ6598-002',
    'https://www.nike.com/t/kd17-basketball-shoes-t6HTr6/FJ9487-002',
    'https://www.nike.com/t/air-jordan-xxxix-university-basketball-shoes-lCjzsl/FQ0213-400',
    'https://www.nike.com/t/kobe-8-big-kids-basketball-shoes-nT1p47/FN0266-400',
    'https://www.nike.com/t/sportswear-tech-fleece-womens-high-waisted-slim-pants-b92xJ9/FV7487-338',
    'https://www.nike.com/t/jordan-flight-fleece-mens-pants-7wCjzb/FV7251-133',
    'https://www.nike.com/t/jordan-flight-fleece-mens-pants-bDdCxC/FV7253-223',
    'https://www.nike.com/t/go-womens-firm-support-high-waisted-7-8-leggings-with-pockets-tGXxmG/DQ5636-338',
    'https://www.nike.com/t/sportswear-phoenix-fleece-womens-over-oversized-crew-neck-sweatshirt-Wj2Rd6/DQ5761-338',
    'https://www.nike.com/t/sportswear-classic-puffer-womens-therma-fit-loose-hooded-jacket-plus-size-6spj0Z/FZ5901-100',
    'https://www.nike.com/t/jordan-flight-fleece-womens-pants-QMCmGn/FV7059-085',
    'https://www.nike.com/t/sportswear-phoenix-fleece-womens-oversized-long-cardigan-plus-size-HZ0hJ0/HF9402-010',
    'https://www.nike.com/t/sportswear-club-fleece-mens-full-zip-hoodie-nR8tst/BV2645-323',
    'https://www.nike.com/t/jordan-chicago-womens-printed-pants-9qzXcb/FV7194-223',
    'https://www.nike.com/t/sportswear-phoenix-fleece-womens-oversized-pullover-hoodie-QnWVHw/DQ5860-632',
    'https://www.nike.com/t/sportswear-tech-fleece-windrunner-womens-jumpsuit-3t0mFj/FB8798-338',
    'https://www.nike.com/t/sportswear-club-fleece-womens-mid-rise-oversized-sweatpants-1MR1ZN/DQ5800-518',
    'https://www.nike.com/t/sportswear-swoosh-puffer-primaloft-womens-therma-fit-oversized-hooded-jacket-zXlcMc/FB8729-218',
    'https://www.nike.com/t/trail-go-womens-firm-support-high-waisted-7-8-leggings-with-pockets-KsXqBz/FN2664-226',
    'https://www.nike.com/t/sportswear-phoenix-plush-womens-oversized-cozy-fleece-full-zip-hoodie-vctXHF/FZ1267-010',
    'https://www.nike.com/t/sportswear-club-fleece-mens-crew-TWcqLw/BV2662-010',
    'https://www.nike.com/t/sportswear-club-fleece-pullover-hoodie-Gw4Nwq/BV2654-043',
    'https://www.nike.com/t/acg-mens-t-shirt-bW3sRj/DQ1815-464',
    'https://www.nike.com/t/standard-issue-mens-dri-fit-basketball-pants-lF6lnX/CK6365-010',
    'https://www.nike.com/t/jordan-sport-jam-mens-warm-up-pants-Mch8rS/FN5850-010',
    'https://www.nike.com/t/sportswear-tech-fleece-mens-shorts-jbdtpn/FB8171-010',
    'https://www.nike.com/t/club-mens-woven-flow-shorts-vw2WpQ/FN3307-010',
    'https://www.nike.com/t/dri-fit-mens-golf-shorts-dxjD21/CU9740-104',
    'https://www.nike.com/t/sportswear-club-mens-graphic-shorts-hQgvng/BV2721-010',
    'https://www.nike.com/t/dri-fit-dna-mens-10-basketball-shorts-FL74Td/DH7160-065',
    'https://www.nike.com/t/m-convertible-diaper-bag-maternity-25l-QLvDt6/DR6083-200',
    'https://www.nike.com/t/air-jordan-11-retro-bred-velvet-womens-shoes-iCg9x5Jv/DB5457-061',
    'https://www.nike.com/t/court-borough-low-recraft-big-kids-shoes-YC85Jqo5/DV5456-122',
    'https://www.nike.com/t/interact-run-womens-road-running-shoes-v5LlQl/FD2292-009',
    'https://www.nike.com/t/al8-womens-shoes-r93WJ3g5/FJ3794-001',
    'https://www.nike.com/t/luka-3-basketball-shoes-R7hgWx/FQ1284-600',
    'https://www.nike.com/t/cosmic-unity-3-basketball-shoes-0zGs9z/DV2757-001',
    'https://www.nike.com/t/gt-jump-2-mens-basketball-shoes-CZpmDQ/DJ9431-501',
    'https://www.nike.com/t/metcon-9-mens-workout-shoes-Tc42zx/DZ2617-801',
    'https://www.nike.com/t/air-max-plus-little-kids-shoes-fkZwCW/CD0610-033',
    'https://www.nike.com/t/air-vapormax-2023-flyknit-mens-shoes-3q1qZg/DV1678-014',
    'https://www.nike.com/t/air-max-1-easyon-little-kids-shoes-JSb44X/DZ3308-115',
    'https://www.nike.com/t/tatum-3-zero-days-off-basketball-shoes-vn4gkx/FZ6598-002',
    'https://www.nike.com/t/kd17-basketball-shoes-t6HTr6/FJ9487-002',
    'https://www.nike.com/t/air-jordan-1-mid-mens-shoes-X5pM09/DQ8426-402',

]

# Loop through each URL and fetch data
all_product_data = []
for url in urls:
    try:
        product_data = fetch_product_data(url)
        all_product_data.append(product_data)
    except Exception as e:
        print(f"Error fetching data from {url}: {e}")

# Save the data to a JSON file
with open('nike_products.json', 'w', encoding='utf-8') as file:
    json.dump(all_product_data, file, ensure_ascii=False, indent=4)

print(f"Data saved for {len(all_product_data)} products.")

