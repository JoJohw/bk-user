/**
 * 租户用户更新邮箱
 */
export interface PatchUserEmailParams {
  id: string,
  is_inherited_email: boolean,
  custom_email: string,
  verification_code?: string,
};

/**
 * 租户用户更新手机号
 */
export interface PatchUserPhoneParams {
  id: string,
  is_inherited_phone: boolean,
  custom_phone: string,
  custom_phone_country_code: string,
  verification_code?: string,
};

/**
 * 租户用户更新头像
 */
export interface PatchUserLogoParams {
  id: string,
  logo: string,
};

/**
 * 租户用户更新密码
 */
export interface PutUserPasswordParams {
  id: string,
  old_password: string,
  new_password: string,
};

/**
 * 租户修改手机号时，发送验证码
 */
export interface postPersonalCenterUserPhoneCaptchaParams {
  phone: string,
  phone_country_code?: string,
};

/**
 * 租户修改邮箱时，发送验证码
 */
export interface postPersonalCenterUserEmailCaptchaParams {
  email: string,
};
/**
 *个人中心-关联账户列表
 */
export interface TenantUser {
  full_name: string,
  id: string,
  logo: string,
  username: string,
  tenant: {
    id: string,
    name: string,
  }
};
export interface CurrentNaturalUser {
  full_name: string,
  id: string,
  tenant_users: TenantUser[],
};

/**
 * 个人中心-关联账户详情
 */
export interface PersonalCenterUsers {
  account_expired_at: string,
  custom_email: string,
  custom_phone: string,
  custom_phone_country_code: string,
  departments: any[],
  email: string,
  extras: object,
  full_name: string,
  id: string,
  is_inherited_email: boolean,
  is_inherited_phone: boolean,
  language: string,
  leaders: any[],
  logo: string,
  phone: string,
  phone_country_code: string,
  time_zone: string,
  username: string,
  [key: string]: any,
};

/**
 * 个人中心-用户可见字段列表
 */

interface CustomFields {
  required: boolean,
  display_name: string,
  isEdit: boolean,
  editable: boolean,
  data_type: string | any,
  value: unknown,
  error: unknown,
  options: any[],
};
export interface PersonalCenterUserVisibleFields {
  builtin_fields: Array<{
    id: number,
    name: string,
    display_name: string,
    data_type: string,
    required: boolean,
    unique: boolean,
    default: string,
    options: any[],
  }>,
  custom_fields: any[] | CustomFields[],
};

/**
 * 个人中心-用户功能特性-当前用户是否支持修改密码
 */
export interface PersonalCenterUserFeature {
  can_change_password: boolean,
  email_update_restriction: string,
  phone_update_restriction: string
};

