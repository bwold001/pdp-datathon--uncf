"use client";

import { useRef } from "react";
import type { VariantProps } from "class-variance-authority";

import { Button, buttonVariants } from "@/components/ui/button";

type FileUploadButtonProps = VariantProps<typeof buttonVariants> & {
  /** Called with the chosen files. Not called when the picker is closed without a choice. */
  onFiles: (files: File[]) => void;
  /** File types the picker offers, as in the input's `accept` attribute. */
  accept?: string;
  multiple?: boolean;
  disabled?: boolean;
  children?: React.ReactNode;
  className?: string;
};

/**
 * A button that opens the file picker. The visible button is the control for keyboard and screen readers;
 * the file input stays hidden.
 */
export function FileUploadButton({
  onFiles,
  accept = ".csv",
  multiple = false,
  disabled = false,
  children,
  variant,
  size,
  className,
}: FileUploadButtonProps) {
  const inputRef = useRef<HTMLInputElement>(null);

  /** Hands the chosen files to `onFiles`, then clears the input so picking the same file again still fires. */
  function handleChange(event: React.ChangeEvent<HTMLInputElement>) {
    const files = Array.from(event.target.files ?? []);
    event.target.value = "";
    if (files.length > 0) onFiles(files);
  }

  return (
    <>
      <Button
        type="button"
        variant={variant}
        size={size}
        className={className}
        disabled={disabled}
        onClick={() => inputRef.current?.click()}
      >
        {children ?? (multiple ? "Choose files" : "Choose file")}
      </Button>
      <input
        ref={inputRef}
        type="file"
        data-slot="file-upload-input"
        accept={accept}
        multiple={multiple}
        disabled={disabled}
        onChange={handleChange}
        hidden
      />
    </>
  );
}
