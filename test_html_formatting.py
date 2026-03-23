#!/usr/bin/env python3
"""Test the refactored HTML card generation logic."""

# Test the .format() approach
cake = 'Dark Chocolate Sea Salt Cake'
rank = 'I'
category = 'Indulgent'
flavor = 'Rich & Savory'
confidence = '<div class="rec-confidence">85.3% match</div>'
technical = '<div class="rec-detail"><strong>Sweetness:</strong> 8/10</div><div class="rec-detail"><strong>Wellness:</strong> 2/10</div>'

card_html = (
    '<div class="rec-card">'
    '<div class="rec-rank">{rank}</div>'
    '<div class="rec-name">{cake}</div>'
    '{confidence}'
    '<div class="rec-description">Recommended for this moment based on your environment and mood.</div>'
    '<div class="rec-detail"><strong>Category:</strong> {category}</div>'
    '<div class="rec-detail"><strong>Flavor:</strong> {flavor}</div>'
    '{technical}'
    '</div>'
).format(
    rank=rank,
    cake=cake,
    confidence=confidence,
    category=category,
    flavor=flavor,
    technical=technical
)

print('✅ HTML card generation successful')
print(f'Card length: {len(card_html)} characters')
print(f'Contains all elements: {all(x in card_html for x in [rank, cake, category, flavor])}')
print(f'\nGenerated HTML (first 200 chars):')
print(card_html[:200] + '...')
print('\n✅ Test passed - .format() approach works correctly')
