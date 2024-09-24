export enum OpenDialogMode {
  Edit = 'edit',
  Verify = 'verify'
};

export enum OpenDialogType {
  email = 'email',
  phone = 'phone'
};

export enum OpenDialogSelect {
  inherit = 'inherit',
  custom = 'custom',
};

export enum OpenDialogResult {
  success = 'success',
  fail = 'danger'
};

export enum EmailEditable {
  YES = 'editable_directly',
  Verify = 'need_verify',
  No = 'not_editable'
};

export enum PhoneEditable {
  YES = 'editable_directly',
  Verify = 'need_verify',
  No = 'not_editable',
};

export enum FormItemPropName {
  inheritEmail = 'inherit-email',
  inheritPhone = 'inherit-phone',
  customEmail = 'custom-email',
  customPhone = 'custom-phone',
  captcha = 'captcha',
};
