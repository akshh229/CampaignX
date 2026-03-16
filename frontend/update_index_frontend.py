import re

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'r', encoding='utf-8') as f:
    text = f.read()

# Add import useToast
to_insert = '''import { useToast } from "@/components/ui/use-toast";\n'''
text = text.replace('import { useState, useCallback }', 'import { useState, useCallback, useEffect }')
text = text.replace('import { RotateCcw } from "lucide-react";\n', 'import { RotateCcw } from "lucide-react";\n' + to_insert)


# Add const { toast } = useToast();
text = text.replace('const Index = () => {', 'const Index = () => {\n  const { toast } = useToast();')


# Add error handling and toaster usage
text = text.replace('console.error("API error", e);', 'toast({ variant: "destructive", title: "API Error", description: String(e) });')

with open('e:/CampaignX/frontend/src/pages/Index.tsx', 'w', encoding='utf-8') as f:
    f.write(text)
