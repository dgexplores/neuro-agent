.PHONY: lock-claude unlock-claude verify-claude

lock-claude:
	@if command -v sha256sum >/dev/null 2>&1; then \
		sha256sum CLAUDE.md > CLAUDE.md.sha256; \
	else \
		shasum -a 256 CLAUDE.md > CLAUDE.md.sha256; \
	fi
	@echo "✅ 已更新 CLAUDE.md.sha256（視為鎖定目標文件）。"

unlock-claude:
	@rm -f CLAUDE.md.sha256
	@echo "⚠️ 已移除校驗檔（暫時解除鎖），記得修改完再 make lock-claude。"

verify-claude:
	@if command -v sha256sum >/dev/null 2>&1; then \
		HASH=$$(sha256sum CLAUDE.md | awk '{print $$1}'); \
	else \
		HASH=$$(shasum -a 256 CLAUDE.md | awk '{print $$1}'); \
	fi; \
	REF=$$(awk '{print $$1}' CLAUDE.md.sha256); \
	if [ "$$HASH" = "$$REF" ]; then echo "✅ 校驗通過"; else echo "❌ 校驗失敗" && exit 1; fi
