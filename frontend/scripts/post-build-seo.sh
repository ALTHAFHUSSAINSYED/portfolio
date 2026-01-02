#!/bin/bash
# Post-build script to ensure sitemap and robots.txt are in build output

echo "📋 Verifying SEO files in build output..."

# Check if sitemap.xml exists
if [ -f "public/sitemap.xml" ]; then
    echo "✅ sitemap.xml found in public/"
    # Copy to build folder (in case react-snap doesn't preserve it)
    cp public/sitemap.xml build/sitemap.xml
    echo "✅ Copied sitemap.xml to build/"
else
    echo "❌ sitemap.xml NOT found in public/"
    exit 1
fi

# Check if robots.txt exists
if [ -f "public/robots.txt" ]; then
    echo "✅ robots.txt found in public/"
    cp public/robots.txt build/robots.txt
    echo "✅ Copied robots.txt to build/"
else
    echo "❌ robots.txt NOT found in public/"
    exit 1
fi

# Verify files in build output
echo ""
echo "📦 Build output verification:"
ls -lh build/sitemap.xml build/robots.txt 2>/dev/null

# Check file contents
echo ""
echo "📄 sitemap.xml first 5 lines:"
head -5 build/sitemap.xml

echo ""
echo "✅ SEO files verified successfully!"
