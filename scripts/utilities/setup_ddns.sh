#!/bin/bash

echo "🌐 Dynamic DNS Setup για Δημόσια IP"
echo "===================================="

# Get current public IP
PUBLIC_IP=$(curl -4 -s ifconfig.me)
echo "📍 Τρέχουσα δημόσια IP: $PUBLIC_IP"

echo ""
echo "🔧 Επιλογές για σταθερή δημόσια πρόσβαση:"
echo ""
echo "1️⃣  STATIC IP από ISP (Προτεινόμενο)"
echo "    - Κάλεσε τον πάροχό σου"
echo "    - Ζήτησε Static Public IP"
echo "    - Κόστος: 5-15€/μήνα"
echo ""
echo "2️⃣  Dynamic DNS (Δωρεάν)"
echo "    - Πήγαινε στο: https://www.noip.com"
echo "    - Δημιούργησε λογαριασμό"
echo "    - Επίλεξε domain: π.χ. mybot.ddns.net"
echo "    - Κατέβασε το No-IP client"
echo ""
echo "3️⃣  Port Forwarding (Απαιτείται)"
echo "    - Μπες στο router: http://192.168.2.1"
echo "    - Port Forward: 8081 -> 192.168.2.7:8081"
echo "    - Έτσι θα μπορείς να συνδεθείς από έξω"

echo ""
echo "📋 Μετά τη ρύθμιση θα έχεις πρόσβαση:"
echo "    http://YOUR-DOMAIN.ddns.net:8081"
echo "    ή http://$PUBLIC_IP:8081 (αν έχεις static IP)"

# Create a script to check public IP changes
cat > check_public_ip.sh << 'EOF'
#!/bin/bash
CURRENT_IP=$(curl -4 -s ifconfig.me)
echo "🌐 Δημόσια IP: $CURRENT_IP"
echo "🔗 FreqTrade: http://$CURRENT_IP:8080"
echo "📱 Local: http://192.168.2.7:8080"
EOF

chmod +x check_public_ip.sh
echo ""
echo "✅ Δημιουργήθηκε script: ./check_public_ip.sh"